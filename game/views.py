import jwt

from django.db.models import Q

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from sheet_music_africa.settings import GAME_ALGORITHM,GAME_SECRET_KEY

from .serializers import GameProfileSerializer,CompetitionSerializer,UserInfoSerializer,LeaderBoardSerializer
from .models import *


# things to do
"""
join competition - post  --done
submit competition score - post  --done

get leaderboard - get --done
get competition - get --done


update profile na remain

"""


class ManageGameRequest(views.APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        page = request.query_params.get('page', None)
        name = request.query_params.get('name',None)

        if page == None:
            data = CompetitionSerializer(
                Competition.objects.filter(status="STA"),
                many=True
            ).data
        
        else:
            try:
                competition = Competition.objects.get(name=name)
                if page == "status":
                    # remaining_time = "Ended"
                    # if competition.status == "STA":
                    remaining_time = competition.update_state()[1]

                    data = {
                        'id':competition.id,
                        'status':competition.status,
                        'time_elasped':remaining_time,
                        'date_started':competition.date_started,
                        'date':competition.date_started.date(),
                        'name':competition.name
                    }

                else:
                    data = LeaderBoardSerializer(
                        competition.get_leader_board(),
                        many=True
                    ).data

            except Competition.DoesNotExist:
                return Response({"msg":"Competition does not exist"},status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
                'data':data
            },status=status.HTTP_200_OK)


    def post(self,request):
        data = request.data
        action = data['action']

        if action == "create":
            new = GameProfileSerializer(data=data)

            if new.is_valid() == True:
                new.save()

                user = GameProfile.objects.get(nickname=new.data['nickname'])
                user.email = user.email.lower()
                user.save()
                user.save_password(data['password'])

                user_info = {
                    "name":data['full_name'],
                    "nickname":data['nickname']
                }

                token = jwt.encode(user_info, GAME_SECRET_KEY, algorithm="HS256")
                return Response({'token':token,'info':UserInfoSerializer(user).data},status=status.HTTP_201_CREATED)

            else:
                return Response({'error':new.errors},status=status.HTTP_400_BAD_REQUEST)

        elif action == "login":
            username = data['username'].lower()
            password = data['password']

            try:
                user = GameProfile.objects.get(Q(nickname=username)|Q(email=username))
                if user.check_password(password) == True:
                    user_info = {
                    "name":user.full_name,
                    "nickname":user.nickname
                    }

                    token = jwt.encode(user_info, GAME_SECRET_KEY, algorithm="HS256")
                    return Response({'token':token,'info':UserInfoSerializer(user).data},status=status.HTTP_200_OK)

            except GameProfile.DoesNotExist:
                pass
            return Response({'error':"Invalid Credentials"},status=status.HTTP_400_BAD_REQUEST)
        
        elif action == "update":
            try:
                print(data['token'])
                user = decodeToken(data['token'])
                if "pic" in data.keys():
                    user.pic = data['pic']
                    user.save()
                    return Response({'msg':"Success","data":user.pic.url})

                return Response({'msg':"attach image"})


            except GameProfile.DoesNotExist:
                return Response({'msg':"Invalid Token"},status=status.HTTP_400_BAD_REQUEST)
        
        elif action == "info":
            try:
                user = decodeToken(data['token'])
                return Response({'msg':"Success","data":UserInfoSerializer(user).data})

            except GameProfile.DoesNotExist:
                return Response({'msg':"Invalid Token"},status=status.HTTP_400_BAD_REQUEST)
                

        else:

            try:
                competiton = Competition.objects.get(Q(name=data['competition'])&Q(status="STA"))

            except Competition.DoesNotExist:
                return Response({'msg':"Competition does not exist"},status=status.HTTP_400_BAD_REQUEST)

            try:
                user = decodeToken(data['token'])

            except GameProfile.DoesNotExist:
                Response({'msg':f"Invalid Token"},status=status.HTTP_400_BAD_REQUEST)


            if action == "join":
                passphrase = data['passphrase']
                if competiton.pass_phrase != passphrase:
                    return Response({'msg':f"Invalid competition phrase - {passphrase}"},status=status.HTTP_400_BAD_REQUEST)

                if competiton not in user.competition.all() and competiton.status != "END":
                    user.competition.add(competiton)

            else:
                if competiton in user.competition.all() and competiton.status == "STA":
                    score = int(data['score'])

                    if score > user.high_score:
                        user.high_score=score

                    if "has_ended" in data.keys():
                        user.score  = 0
                    else:
                        user.score = score

                    user.save()
            
            return Response({"state":competiton.status,'time_elasped':competiton.update_state()[1]},status=status.HTTP_200_OK)
            

def decodeToken(token):
    my_token = jwt.decode(token, GAME_SECRET_KEY, algorithms="HS256")
    return GameProfile.objects.get(nickname=my_token['nickname'])
