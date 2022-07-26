from cProfile import Profile
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render

from rest_framework import viewsets, pagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import  generics, views, status 

from utility.utils import processNewGenre

from .serializer import *
from .models import *

from composer.models import FollowComposer, UserPaymentHistory, UserPaymentLog, ComposerProfile,ComposerAccount
from sheet_music_africa.settings import MAIN_SITE_ADDRESS,BOTREGEX,LOGO_URL,MINIMUM_SCORE_PRICE, PAYMENT_SECRET_KEY, FLUTTER_WAVE_COUNTRIES, FLUTTER_URL, AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_REGION_NAME, ACCOUNT_NAME

import requests,math,datetime,decimal,re

import boto3
from botocore.exceptions import ClientError
# from botocore.config import Config


class SitePagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 10000


class GenreView(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.filter(verified=True)


def ourRecommendations(queryset=None,song=None,user=None):
    if song != None:
        genre = [g.id for g in song.genre.all()]
        queryset = SheetMusic.objects.filter(Q(genre__in=genre)&Q(verified=True)&Q(deleted=False)).distinct()

    if queryset == None:
        queryset = removePurchasedSong(user)

    return queryset.order_by("-point")


def removePurchasedSong(user):
    try:
        purchased_score = [sale.score for sale in Score_sale.objects.filter(
            Q(user=user) & Q(purchased=True))]
    except:
        purchased_score = []

    song_make_we_go_remove = []
    purchased_score_song = []

    for score in purchased_score:
        song = score.main_song
        if song not in purchased_score_song:
            song_score = Score.objects.filter(main_song=song)
            our_count = 0
            for score in song_score:
                if score in purchased_score:
                    our_count += 1

            if our_count == song_score.count():
                song_make_we_go_remove.append(song.id)

    return SheetMusic.objects.filter(
        Q(deleted=False) & Q(verified=True)&Q(rejected=False)).exclude(pk__in=song_make_we_go_remove)



class SheetMusicView(viewsets.ModelViewSet):
    serializer_class = SheetMusicSerializer
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = SitePagination

    def retrieve(self, request, pk=None):
        song = SheetMusic.objects.get(pk=pk)
        if(song.deleted == False):
            return Response({
                'data': SheetMusicSerializer(song).data,
                'similar':SheetMusicSerializer(ourRecommendations(None,song,None),many=True).data
            })

        return Response({'data': None})

    def get_queryset(self):
        query = self.request.query_params.get('query', None)
        genre = self.request.query_params.get('genre', None)
        option = self.request.query_params.get('option', None)
        username = self.request.query_params.get('username', None)

        if username == None:
            queryset = removePurchasedSong(self.request.user)

            if genre != None:
                try:
                    current_genre = Genre.objects.get(name__iexact=genre)
                    queryset = queryset.filter(genre=current_genre)
                except Genre.DoesNotExist:
                    return []

            if query != None:
                queryset = queryset.filter(name__icontains=query)

            if option != None:
                if option == "trending":
                    queryset = ourRecommendations(queryset,None)
                else:
                    queryset = queryset.filter(name__startswith=option)
            return queryset
        else:
            current_user = User.objects.get(username=username)
            return SheetMusic.objects.filter(Q(composer=current_user) & Q(deleted=False) & Q(verified=True))

    def perform_create(self, serializer):
        client_data = self.request.data

        if "new_genre" in client_data.keys():
            processNewGenre(client_data['new_genre'])


        genre = client_data['genre'].split(",")
        thumbnail = client_data['thumbnail']
        main_sheet = serializer.save(
            composer=self.request.user, genre=genre, thumbnail=thumbnail)

        if "tags" in client_data.keys():
            main_sheet.tags = client_data['tags']

        music_scores = client_data['music_scores'].split(',')


        for score in music_scores:
            current_score_info = score.split(':')
            price = current_score_info[1]

            if float(price) >= MINIMUM_SCORE_PRICE:
                new_score = Score()
                new_score.main_song = main_sheet
                new_score.name = current_score_info[0]
                new_score.price = decimal.Decimal(price)
                new_score.sheet = client_data['file_%s' % current_score_info[2]]
                new_score.save()
            else:
                main_sheet.delete()


    def update(self, request, pk=None):

        main_sheet = SheetMusic.objects.get(pk=pk)
        if request.user == main_sheet.composer:
            data = self.request.data
            sheet_scores = []

            if 'audio' in data.keys():
                main_sheet.audio.delete()

            if "tags" not in data.keys():
                    main_sheet.tags = ""

            serializer = SheetMusicSerializer(main_sheet, data=data)
            if serializer.is_valid():
                main_sheet.genre.clear()

                main_sheet = serializer.save()

                if data['genre'] != "":
                    genre = [int(i) for i in data['genre'].split(",")]
                    for i in genre:
                        current_genre = Genre.objects.get(pk=i)
                        try:
                            main_sheet.genre.add(current_genre)
                        except:
                            pass
            else:
                if 'name' in serializer.errors.keys():
                    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            music_scores = data['music_scores'].split(',')
            for score in music_scores:
                current_score_info = score.split(':')

                id = current_score_info[2]
                file_name = 'file_%s' % id
                try:
                    score = Score.objects.get(pk=int(id))
                    #check if song is rejected
                    if main_sheet.rejected == True:
                        #if yes allow them to edit pdf
                        if file_name in data.keys():
                            score.sheet.delete() #delete former pdf in storage
                            score.sheet = data[file_name]
                            score.rejected = False

                            main_sheet.rejected = False
                            main_sheet.verified = False

                except Score.DoesNotExist:
                    score = Score()
                    score.main_song = main_sheet
                    if file_name in data.keys():
                        score.sheet = data[file_name]
                        main_sheet.verified = False

                score.name = current_score_info[0]
                score.price = current_score_info[1]

                score.save()
                sheet_scores.append(score.id)
                
                main_sheet.save()

            main_sheet.update_score(sheet_scores)
            return Response({'song': SheetMusicSerializer(main_sheet).data})

        else:
            return Response({'msg': 'you cannot edit this song'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        sheet = SheetMusic.objects.get(pk=pk)

        for score in Score.objects.filter(main_song=sheet):
            try:
                score_sale = Score_sale.objects.get(score=score)
                if score_sale.purchased == False:
                    score_sale.score.sheet.delete()
                    score_sale.score.delete()
            except Score_sale.DoesNotExist:
                score.sheet.delete()
                score.delete()

        if Score.objects.filter(main_song=sheet).count() == 0:
            sheet.delete()
        else:
            sheet.deleted = True
            sheet.save()

        return Response({'msg': 'successful'})


def get_score_purchased(song, user):
    purchased_string = ""
    song_score = Score.objects.filter(main_song=song)
    purchased_score = Score_sale.objects.filter(
        Q(score__in=song_score) & Q(purchased=True) & Q(user=user))
    for song in purchased_score:
        purchased_string += '%s:%d,' % (song.score.name, song.score.id)

    return purchased_string


@api_view(['GET'])
def getMoreInfoOnSheetMusic(request, id):

    # get sheet rating and if user is following composer
    data = {
        'is_following_composer': False,
        'rating': 0,
        'id': None
    }
    current_sheet = SheetMusic.objects.get(id=id)

    try:
        user = User.objects.get(pk=request.user.pk)
        try:
            data['rating'] = My_review.objects.get(
                Q(user=user) & Q(sheet=current_sheet)).rating
            data['id'] = My_review.objects.get(
                Q(user=user) & Q(sheet=current_sheet)).id
        except My_review.DoesNotExist:
            pass
        try:
            owner_of_sheet = ComposerProfile.objects.get(
                user=current_sheet.composer)
            you = ComposerProfile.objects.get(user=user)
            FollowComposer.objects.get(
                Q(main_composer=owner_of_sheet) & Q(other_composer=you))
            data['is_following_composer'] = True
        except FollowComposer.DoesNotExist:
            pass
    except User.DoesNotExist:
        pass

    return Response(data)


class CartView(viewsets.ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        queryset = Score_sale.objects.filter(purchased=False)
        try:
            user = User.objects.get(pk=self.request.user.pk)
            queryset = queryset.filter(user=user)
        except User.DoesNotExist:
            pass
        return queryset

    def perform_create(self, serializer):
        pass


    def destroy(self, request, pk=None):
        current_cart = Score_sale.objects.get(pk=pk)
        if current_cart.user == request.user and current_cart.purchased == False:
            current_cart.delete()
            return Response({'msg': 'successful'})

        return Response({'msg': 'failed'})


class AddToCart(views.APIView):
    def post(self, request):
        form = request.POST
        user = request.user
        cart_list = request.POST['cart_list']

        if cart_list != "":
            cart_list = cart_list.split(",")

            for cart_id in cart_list:
                current_score = Score.objects.get(pk=int(cart_id))

                try:
                    Score_sale.objects.get(
                        Q(user=user) & Q(score=current_score))
                except Score_sale.DoesNotExist:
                    if(current_score.main_song.composer != user):
                        new = Score_sale()
                        new.user = user
                        new.score = current_score
                        new.save()

        all_cart = Score_sale.objects.filter(Q(user=user) & Q(purchased=False))
        return Response({'cart': CartSerializer(all_cart, many=True).data})


class SheetReviewView(viewsets.ModelViewSet):
    serializer_class = SheetMusicReviewSerializer
    pagination_class = SitePagination

    def get_queryset(self):
        sheet = self.request.query_params.get('sheet', None)
        user = self.request.query_params.get('user', None)
        queryset = My_review.objects.all()

        if sheet != None:
            current_sheet = SheetMusic.objects.get(name__iexact=sheet)
            queryset = queryset.filter(sheet=current_sheet)

        if user != None:
            current_user = User.objects.get(username__iexact=user)
            queryset = queryset.filter(user=current_user)

        return queryset

    def perform_create(self, serializer):
        data = self.request.data
        sheet = SheetMusic.objects.get(pk=int(data['sheet']))
        user = self.request.user
        rating = int(data['rating'])

        serializer.save(sheet=sheet, user=user, rating=rating)
        sheet.updateRating()

    def update(self, request, pk=None):
        current_review = My_review.objects.get(pk=pk)
        current_review.rating = request.data['rating']
        current_review.save()
        current_review.sheet.updateRating()

        sheet = current_review.sheet
        return Response({'rating': sheet.star, 'rating_count': sheet.rating})


class getSales(generics.ListAPIView):
    serializer_class = SheetSaleSerializer
    pagination_class = SitePagination

    def get_queryset(self):
        try:
            user = User.objects.get(pk=self.request.user.pk)
            queryset = SheetMusic.objects.filter(
                Q(deleted=False) & Q(composer=user))
            return queryset
        except:
            return []


class GoToDigitalLibary(generics.ListAPIView):
    serializer_class = SheetMusicSerializer
    pagination_class = SitePagination

    def get(self,request):
        queryset = []
        status = "purchased"

        try:
            user = request.user
            my_songs = Score_sale.objects.filter(
                Q(user=user)
                &Q(purchased=True)
                &Q(downloadable=True)
            )
            for song in my_songs:
                current_song = song.score.main_song
                if current_song not in queryset:
                    queryset.append(current_song)
            
            if len(queryset) == 0:
                queryset = queryset = ourRecommendations(None,None,user)
                status = "recommendation"
        except:
            return Response({'data':[]})

        return Response({'data':SheetMusicSerializer(queryset,many=True).data,'status':status})

    def get_queryset(self):
        pass
        


# Views for processing payments
@api_view(['POST'])
def get_checkout_link(request):
    user = request.user
    # Getting all of the item that are in cart currently
    user_cart = Score_sale.objects.filter(Q(user=user) & Q(purchased=False))
    total_price = sum([i.score.price for i in user_cart])
    total_price = math.ceil(total_price)


    #creating or getting existing payment history
    try:
        history = UserPaymentHistory.objects.get(
            Q(user=user) & Q(verified=False))
    except UserPaymentHistory.DoesNotExist:
        history = UserPaymentHistory()
        history.user = user
        history.save()
    
    history.price = total_price

    #adding individual cart item to payment history
    for cart in user_cart:
        price = cart.score.price
        percentage = cart.score.main_song.percentage
        cart.purchased_price = price
        cart.purchased_percentage = percentage
        cart.seller_revenue = price*percentage // 100
        cart.save()

        history.cart_item.add(cart.id)
    
    history.save()

    # makeing request to get payment link from flutterwave
    bearer = 'Bearer %s' % PAYMENT_SECRET_KEY

    URL = "%spayments" % FLUTTER_URL
    redirect = "https://sheetmusicafrica.com"
    headers = {'Authorization': bearer, "Content-Type": "Application/json"}
    data = {
        "tx_ref": str(history.pk),
        "amount": total_price,
        "currency": "USD",
        "redirect_url": redirect,
        "payment_options": "card",
        "customer": {
            "email": user.email,
            "phonenumber": "",
            "name": "%s %s" % (user.first_name, user.last_name)
        },
        "customizations": {
            "title": "Sheet Music Africa",
            "description": "Make payment to continue",
            "logo": LOGO_URL
        }
    }
    r = requests.post(url=URL, json=data, headers=headers)
    data = r.json()

    return Response({'price': total_price, 'link': data['data']['link'], 'id': history.pk})



@api_view(['GET'])
def verifyPayment(request):

    user = request.user

    if user.is_anonymous == False:
        try:
            current_payment_history = UserPaymentHistory.objects.get(Q(user=user)&Q(verified=False))

            URL = '%stransactions' % (FLUTTER_URL)
            bearer = 'Bearer %s' % PAYMENT_SECRET_KEY

            headers = {
                'Content-Type': 'application/json',
                'Authorization': bearer
            }

            params = {
                'tx_ref':str(current_payment_history.id),
                'status':'successful'
            }

            r = requests.get(url=URL, headers=headers, params=params)
            resp = r.json()
            data = resp['data'][0]

            #Verifying payment here
            if data['currency'] == current_payment_history.currency:
                if data['amount'] >= math.ceil(current_payment_history.price):
                    for purchased_score in current_payment_history.cart_item.all():

                        purchased_score.purchased = True
                        purchased_score.downloadable = True
                        purchased_score.save()

                        purchased_song = purchased_score.score.main_song

                        #owner of song that was purchased
                        user = purchased_song.composer

                        # giving monetary value to both the us and the composer
                        seller_earned_value = decimal.Decimal(
                            purchased_score.purchased_price * purchased_song.percentage)/100

                        our_earned_value = decimal.Decimal(
                            purchased_score.purchased_price - seller_earned_value)

                        #remove this shit
                        sheet_music_africa_account = User.objects.get(
                            username=ACCOUNT_NAME)

                        try:
                            sheet_music_composer_profile = ComposerProfile.objects.get(
                                user=sheet_music_africa_account)
                        except ComposerProfile.DoesNotExist:
                            sheet_music_composer_profile = ComposerProfile(
                                user=sheet_music_africa_account)
                            sheet_music_composer_profile.save()

                        sheet_music_composer_profile.all_time_sales += our_earned_value
                        sheet_music_composer_profile.current_sales += our_earned_value

                        sheet_music_composer_profile.save()

                        composer = ComposerProfile.objects.get(user=user)

                        composer.all_time_sales += seller_earned_value
                        composer.current_sales += seller_earned_value

                        composer.save()

                        today = datetime.datetime.now().date()

                        seller_payment_account_info = ComposerAccount.objects.get(composer=composer)

                        try:
                            payment_current_payment_history = UserPaymentLog.objects.get(
                                Q(user=user) & Q(date=today) & Q(log_type="sales"))
                            payment_current_payment_history.price += seller_earned_value
                        except UserPaymentLog.DoesNotExist:
                            payment_current_payment_history = UserPaymentLog()
                            payment_current_payment_history.user = user
                            payment_current_payment_history.price = seller_earned_value
                            payment_current_payment_history.log_type = "sales"

                            if seller_payment_account_info.email != "":
                                payment_current_payment_history.bank_paid_to = seller_payment_account_info.account_number
                                payment_current_payment_history.bank_name_paid_to = seller_payment_account_info.bank_name
                            else:
                                payment_current_payment_history.email_paid_to = seller_payment_account_info.email
                            

                        payment_current_payment_history.save()

                    current_payment_history.verified = True
                    current_payment_history.save()
                    purchased_song.update_percentage()

                    return Response({'msg': 'successful'})

        except UserPaymentHistory.DoesNotExist:
            return Response({'msg': 'unverified'})

    return Response({'msg': 'no user'})
    

# think of a way to take our percentage from song sales
@api_view(['POST'])
def withdrawlRevenue(request):
    pass
    # user = request.user

    # if user.composer.country in FLUTTER_WAVE_COUNTRIES:
    #     URL = "%stransfers"%FLUTTER_URL

    #     bearer = 'Bearer %s' % PAYMENT_SECRET_KEY

    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Authorization': bearer
    #     }

    #     data = {
    #         "account_bank": "044",
    #         "account_number": "0690000040",
    #         "amount": 5500,
    #         "narration": "Sheet Music Payout",
    #         "currency": "USD",
    #         "reference": "akhlm-pstmnpyt-rfxx007_PMCKDU_1",
    #         "callback_url": "https://webhook.site/b3e505b0-fe02-430e-a538-22bbbce8ce0d",
    #         "debit_currency": "USD"
    #     }

    #     r = requests.get(url=URL, json=data, headers=headers)
    #     data = r.json()

    #     return Response({})

    # else:
    #     # Use paypal to make payout
    #     return Response({})


@api_view(['GET'])
def downloadScore(request, id):
    score = Score.objects.get(pk=id)
    user = request.user
    profile = ComposerProfile.objects.get(user=user)

    if user == score.main_song.composer or profile.can_verify == True:
        return Response({'link': create_presigned_url('private/%s' % score.sheet.name, 300)})

    try:
        purchased_score = Score_sale.objects.get(
            Q(user=user)
            & Q(score=score)
            & Q(purchased=True)
            & Q(downloadable=True)
        )
        url = create_presigned_url('private/%s' % score.sheet.name, 300)
        return Response({'link': url})

    except Score_sale.DoesNotExist:
        return Response({'failed'})


def create_presigned_url(object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3', region_name=AWS_S3_REGION_NAME,
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': AWS_STORAGE_BUCKET_NAME,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        print("s3 error :: ", e)
        return None

    # The response contains the presigned URL
    print('s3 response - ', response)
    return response



"""
get unverified song
accept or reject song
"""
@api_view(['GET'])
def getUnverifiedSongs(request):
    print("current user ",request.user)
    profile = ComposerProfile.objects.get(user=request.user)
    if profile.can_verify == True:
        songs = SheetMusic.objects.filter(Q(deleted=False)&Q(verified=False)&Q(rejected=False))
        return Response({'data':SheetMusicSerializer(songs,many=True).data})
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def markSong(request):
    profile = ComposerProfile.objects.get(user=request.user)
    if profile.can_verify == True:
        data = request.POST
        current_song = SheetMusic.objects.get(pk=data['id'])
        response = data['response']

        if response == "verified":
            current_song.verified = True
        else:
            current_song.rejected = True
            current_song.verified = False

            rejected_songs = data['rejected_songs'].split(',')
            for song_id in rejected_songs:
                current = Score.objects.get(id=song_id)
                current.rejected = True
                current.save()

        current_song.save()

        return  Response({'msg':'done'})

    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


#Link Sharing
@api_view(['get'])
def redirect_to_frontend(request):
    return HttpResponseRedirect(MAIN_SITE_ADDRESS)

@api_view(['get'])
def redirect_composer_to_frontend(request,path):
    url = f"{MAIN_SITE_ADDRESS}/c/{path}"
    try:
        user = User.objects.get(username=path)
        try:
            profile = ComposerProfile.objects.get(user=user)
            image = None
            if profile.pic != None:
                image = profile.pic.url

            if re.search(f"^{BOTREGEX}",request.META['HTTP_USER_AGENT']) != None:
                return render(request,'musicStore/crawler.html',{
                    'title':f"{user.first_name} {user.last_name}",
                    'discription':f"{profile.discription}"[:64],
                    'url':url,
                    'image':image
                })

        except ComposerProfile.DoesNotExist:
            pass

    except SheetMusic.DoesNotExist:
        pass

    return HttpResponseRedirect(url)

@api_view(['get'])
def redirect_song_to_frontend(request,path=None,param=None):
    url = f"{MAIN_SITE_ADDRESS}/c/{path}/{param}"
    try:
        pk = int(param.split("-")[-1])
        song = SheetMusic.objects.get(pk=pk)


        if re.search(f"^{BOTREGEX}",request.META['HTTP_USER_AGENT']) != None:
            if song.deleted == False:
                context ={
                    'url':url,
                }
                context['title'] = f"{song.name}"
                context['discription'] = f"{song.discription}"[:65]
                if song.thumbnail:
                    context['image'] = song.thumbnail.url
                if song.audio:
                    context['audio'] = song.audio.url

                return render(request,'musicStore/crawler.html',context)

    except SheetMusic.DoesNotExist:
        pass

    return HttpResponseRedirect(url)

    
