from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from django.template.loader import get_template

from rest_framework import viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import permissions, generics, views, status

from .models import *
from .serializer import *
from payout.payout import withdrawlRevenue, get_paypal_access_token


from musicStore.models import SheetMusic, Score_sale, Score
from musicStore.serializer import ScoreSerializer

from sheet_music_africa.settings import PAYOUT_DAY, PAYMENT_LANDMARK, PAYMENT_SECRET_KEY, FLUTTER_URL

import datetime
import requests

from xhtml2pdf import pisa

from io import BytesIO


class RegisterUser(views.APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        form = request.POST
        user_email = form['email'].lower()
        password = form['password']
        username = form['username']

        try:
            User.objects.get(username=username)
            return Response({'msg': 'User with that username already Exist'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            pass

        try:
            User.objects.get(email=user_email)
            return Response({'msg': 'User with that email already Exist'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            if password == form['confirm_password']:
                new_user = User()
                new_user.first_name = form['first_name']
                new_user.last_name = form['other_names']
                new_user.email = user_email
                new_user.username = username

                new_user.set_password(form['password'])
                new_user.save()

                # making users composer profile
                if new_user != None:
                    user_composer_profile = ComposerProfile(
                        user=new_user
                    )
                    user_composer_profile.country = form['country']
                    user_composer_profile.country_short_code = form['country_code']
                    user_composer_profile.save()

                    return Response({'msg': 'created'}, status=status.HTTP_201_CREATED)

        return Response({'msg': 'failed'}, status=status.HTTP_400_BAD_REQUEST)


class GetComposerAccountInfo(views.APIView):
    def get(self, request):
        composer = ComposerProfile.objects.get(
            user=request.user)

        country = composer.country_short_code
        try:
            composer_account = ComposerAccount.objects.get(composer=composer)
            bank_name = composer_account.bank_name
            account_number = formatAccountNumber(
                composer_account.account_number)
        except ComposerAccount.DoesNotExist:
            bank_name = ""
            account_number = ""

        URL = '%sbanks/%s' % (FLUTTER_URL, country) #possible ssrf through country entry
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % PAYMENT_SECRET_KEY
        }

        r = requests.get(url=URL, headers=headers)
        data = r.json()

        return Response({
            'current_bank': bank_name,
            'account_number': account_number,
            'banks': data['data']
        })

    def post(self, request):
        data = request.POST
        user = request.user

        bank = data['bank']
        account_number = data['account_number']
        bank_code = data['bank_code']

        user_profile = ComposerProfile.objects.get(user=user)

        try:
            account = ComposerAccount.objects.get(composer=user_profile)
            account.bank_name = bank
            account.bank_code = bank_code
            if "*" not in account_number:
                account.account_number = account_number

        except ComposerAccount.DoesNotExist:
            account = ComposerAccount()
            account.composer = user_profile
            account.bank_name = bank
            account.bank_code = bank_code
            account.account_number = account_number
        account.save()

        return Response({'current_bank': account.bank_name, 'account_number': formatAccountNumber(account.account_number)})


def formatAccountNumber(account_number):
    returnedNumber = ""
    length_of_account_number = len(account_number)
    returnedNumber += account_number[0:2]
    length_of_star = len(account_number) - 5

    while length_of_star > 0:
        returnedNumber += "*"
        length_of_star -= 1

    returnedNumber += account_number[length_of_account_number -
                                     3:length_of_account_number]

    return returnedNumber


class ChangePassword(views.APIView):
    def post(self, request):
        data = request.data
        user = request.user

        old_password = data['old_password']
        new_password = data['new_password']
        confirm_password = data['confirm_password']

        getUser = authenticate(username=user.username, password=old_password)

        if getUser is not None:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                return Response({'msg': 'successful'})
            else:
                return Response({'msg': 'passwords dont match'})

        return Response({'msg': 'Invalid password'})


class ComposerView(viewsets.ModelViewSet):
    serializer_class = ComposerSerializer

    def get_queryset(self):
        queryset = ComposerProfile.objects.all()
        composer = self.request.query_params.get('composer', None)

        if composer != None:
            current_composer = composer.split(" ")
            if len(current_composer) == 1:
                composer_user_account = User.objects.get(Q(first_name__icontains=current_composer[0])
                                                         | Q(last_name__icontains=current_composer[0]))
            else:
                composer_user_account = User.objects.get(Q(first_name__icontains=current_composer[0])
                                                         | Q(last_name__icontains=current_composer[1]))

            queryset = queryset.filter(user__in=[composer_user_account])

        return queryset

    def retrieve(self, request, pk=None):
        user = User.objects.get(username=pk)
        user_profile = ComposerProfile.objects.get(user=user)
        subscribed = False

        try:
            logInUser = User.objects.get(pk=request.user.pk)
            other_composer = ComposerProfile.objects.get(user=logInUser)
            try:
                relationship = FollowComposer.objects.get(
                    Q(main_composer=user_profile)
                    & Q(other_composer=other_composer)
                )
                subscribed = True
            except FollowComposer.DoesNotExist:
                pass
        except User.DoesNotExist:
            pass

        return Response({'data': ComposerSerializer(user_profile).data, 'subscribed': subscribed})

    def update(self, request, pk=None):
        user = request.user
        current_composer = ComposerProfile.objects.get(pk=pk)

        if current_composer.user == user:
            # continue from here when you get back from school
            offline = False
            data = request.data
            print("data keys -", data.keys())

            try:
                if "background_image" in data.keys():
                    current_composer.background_image.delete()

                if "pic" in data.keys():
                    current_composer.pic.delete()
            except:
                return Response({'msg':'failed to connect to aws'},status=status.HTTP_408_REQUEST_TIMEOUT)
                

            if 'fullname' in data.keys():
                name = data['fullname'].split(" ")
                last_name = ""
                first_name = name[0]
                user.first_name = first_name
                name.remove(first_name)

                for i in name:
                    last_name += " %s" % i

                user.last_name = last_name

            if 'email' in data.keys():
                user.email = data['email'].lower()

            user.save()

            serializer = ComposerSerializer(current_composer, data=data)
            if serializer.is_valid():
                serializer.save()
            current_composer = ComposerProfile.objects.get(pk=pk)

            return Response({'data': ComposerSerializer(current_composer).data})

        return Response({'data': {'msg':'ode'}}, status=status.HTTP_400_BAD_REQUEST)


class ComposerRelationshipView(viewsets.ModelViewSet):
    serializer_class = ComposerRelationshipSerializer

    def get_queryset(self):
        queryset = FollowComposer.objects.all()
        option = self.request.query_params.get('option', None)

        try:
            user = User.objects.get(pk=self.request.user.pk)

            if option != None:
                if option == "following":
                    queryset = queryset.filter(main_composer=user.composer)
                else:
                    queryset = queryset.filter(other_composer=user.composer)
        except User.DoesNotExist:
            pass

        return queryset


class WithdrawlRevenue(views.APIView):
    def get(self, request):
        user = User.objects.get(pk=1)  # request.user
        user_profile = ComposerProfile.objects.get(user=user)

        try:
            account = ComposerAccount.objects.get(composer=user_profile)
            amount = user_profile.current_sales
            status = withdrawlRevenue(account, amount)

            if status == "successs":
                return Response({
                    'type': 'success',
                    'msg': 'Payout has been made you will recieve your money in less than 48 hours'
                })

            else:
                return Response({
                    'type': 'error',
                    'msg': 'payout failed, please try again later'
                })
        except ComposerAccount.DoesNotExist:
            return Response({
                'type': 'error',
                'msg': "Invalid operation, you don't have an account"
            })


def getPurchasedSong(song, user):
    sale_string = ""
    song_scores = Score.objects.filter(main_song=song)
    score_sale = Score_sale.objects.filter(
        Q(user=user) & Q(score__in=song_scores))
    for sale in score_sale:
        sale_string += '%d,' % sale.score.id

    return sale_string[0:len(sale_string)-1]


class getUser(views.APIView):
    def get(self, request):
        user = request.user
        composer = ComposerProfile.objects.get(user=user)
        digital_libary = []
        purchased_sheet_id = []
        purchased_songs = Score_sale.objects.filter(
            Q(user=user) & Q(purchased=True))

        for song in purchased_songs:
            c_song = song.score.main_song.pk
            if(c_song not in purchased_sheet_id):
                purchased_sheet_id.append(c_song)

            digital_libary.append(song.score.id)

        try:
            pic = composer.pic.url
        except:
            pic = None

        return Response({
            'pic': pic,
            'name': '%s %s' % (user.first_name, user.last_name),
            'email': user.email,
            'id': composer.id,
            'admin':composer.can_verify,
            'username': user.username,
            'digital_libary': digital_libary,
            'purchased_sheet': purchased_sheet_id
        })


@api_view(['GET'])
def getPurchasedScore(request, song):
    user = request.user
    profile = ComposerProfile.objects.get(user=user)
    current_song = SheetMusic.objects.get(pk=song)
    song_scores = Score.objects.filter(main_song=current_song)

    if user == current_song.composer or profile.can_verify == True:
        return Response({'results': ScoreSerializer(song_scores, many=True).data, 'song': current_song.name})


    for score in song_scores:
        try:
            score_sale = Score_sale.objects.get(
                Q(user=user)
                & Q(score=score)
                & Q(purchased=True)
                & Q(downloadable=True))
        except Score_sale.DoesNotExist:
            song_scores = song_scores.exclude(pk=score.id)

    return Response({'results': ScoreSerializer(song_scores, many=True).data, 'song': current_song.name})


class getPaymentinfo(views.APIView):
    def get(self, request):
        composer = ComposerProfile.objects.get(user=request.user)
        total_sales = composer.all_time_sales
        current_sales = composer.current_sales
        withdrawl_revenue = total_sales - current_sales

        today = datetime.datetime.now().date()
        day = today.day
        month = today.month
        year = today.year

        print("my day is ", day, ' ', PAYOUT_DAY)
        if day > PAYOUT_DAY:
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1

        payout_day = "%s/%d/%d" % (PAYOUT_DAY, month, year)

        return Response({
            'landmark': PAYMENT_LANDMARK,
            'nextPayout': payout_day,
            'total_sales': total_sales,
            'current_sales': current_sales,
            'withdrawl_revenue': withdrawl_revenue
        })


class getPaymentHistory(views.APIView):
    def get(self, request):
        user = request.user
        all_history = UserPaymentLog.objects.filter(user=user).order_by("-date")[:10]

        return Response({'data': PaymentLogSerializer(all_history, many=True).data})


@api_view(['POST'])
def mangeComposerRelationship(request):
    subscribed = False
    data = request.POST
    user_profile = ComposerProfile.objects.get(
        user=request.user)  # requested user composer profile

    main_user = User.objects.get(email=data['uemail'].lower())
    main_user_profile = ComposerProfile.objects.get(
        user=main_user)  # composer you are subscribing to

    try:
        current_relationship = FollowComposer.objects.get(
            Q(main_composer=main_user_profile)
            & Q(other_composer=user_profile)
        ).delete()
    except FollowComposer.DoesNotExist:
        current_relationship = FollowComposer()
        current_relationship.main_composer = main_user_profile
        current_relationship.other_composer = user_profile
        current_relationship.save()
        subscribed = True

    subscribers = FollowComposer.objects.filter(
        main_composer=main_user_profile).count()

    return Response({'status': subscribed, 'subscribers': subscribers})


class GeneratePdf(views.APIView):
    def get(self, request, *args, **kwargs):

        # collecting dates
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        # collecting user sales information
        user = request.user

        username = "%s %s" % (user.first_name, user.last_name)
        user_song = SheetMusic.objects.filter(verified=True)
        user_score = Score.objects.filter(main_song__in=user_song)

        withdrawl_report = UserPaymentLog.objects.filter(
            Q(user=user) & Q(log_type="withdrawl"))
        song_sales = Score_sale.objects.filter(
            Q(score__in=user_score) & Q(purchased=True))

        if start_date != None:
            # reformat start date
            print(start_date)
            withdrawl_report = withdrawl_report.filter(date__gte=start_date)
            song_sales = song_sales.filter(
                date_purchased__gte=start_date)

        if end_date != None:
            withdrawl_report = withdrawl_report.filter(date__lte=end_date)
            song_sales = song_sales.filter(
                date_purchased__lte=end_date)

        # getting the template
        pdf = render_to_pdf('composer/invoice.html', {
            'username': username,
            'withdrawl_report': withdrawl_report,
            'song_sales': song_sales
        })

        # rendering the template
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=sheet_music_africa_report.pdf'

        return response


def render_to_pdf(template_src, context_dict={}):

    # code from: https: // www.simplifiedpython.net/html-to-pdf-django-tutorial/

    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    # This part will create the pdf.
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


@api_view(['GET'])
def testpaypal(request):
    data = get_paypal_access_token()
    return Response(data)
