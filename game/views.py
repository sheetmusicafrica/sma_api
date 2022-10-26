import jwt

from django.db.models import Q

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from sheet_music_africa.settings import GAME_ALGORITHM,GAME_SECRET_KEY

from .serializers import GameProfileSerializer,CompetitionSerializer,UserInfoSerializer
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
        id = request.query_params.get('id',None)

        if page == None:
            data = CompetitionSerializer(
                Competition.objects.filter(status="STA"),
                many=True
            ).data
        
        else:
            try:
                competition = Competition.objects.get(Q(id=int(id))&Q(status="STA"))
                data = GameProfileSerializer(
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
                user.save_password(data['password'])

                user_info = {
                    "name":data['full_name'],
                    "nickname":data['nickname']
                }

                token = jwt.encode(user_info, GAME_SECRET_KEY, algorithm=GAME_ALGORITHM)
                return Response({'token':token,'info':UserInfoSerializer(user).data},status=status.HTTP_201_CREATED)

            else:
                return Response({'error':new.errors},status=status.HTTP_400_BAD_REQUEST)

        elif action == "login":
            username = data['username']
            password = data['password']

            try:
                user = GameProfile.objects.get(Q(nickname=username)|Q(email=username))
                if user.check_password(password) == True:
                    user_info = {
                    "name":user.full_name,
                    "nickname":user.nickname
                    }

                    token = jwt.encode(user_info, GAME_SECRET_KEY, algorithm=GAME_ALGORITHM)
                    return Response({'token':token,'info':UserInfoSerializer(user).data},status=status.HTTP_200_OK)

            except GameProfile.DoesNotExist:
                pass
            return Response({'error':"Invalid Credentials"},status=status.HTTP_400_BAD_REQUEST)
        
        elif action == "update":
            try:
                user = decodeToken(data['token'])
                if "pic" in data.keys():
                    if user.pic != None:
                        user.pic.delete()

                    user.pic = data['pic']
                    user.save()
                    return Response({'msg':"Success"})

                return Response({'msg':"attach image"})


            except GameProfile.DoesNotExist:
                Response({'msg':f"Invalid Token"},status=status.HTTP_400_BAD_REQUEST)
                

        else:

            try:
                competiton = Competition.objects.get(Q(id=int(data['competition']))&Q(status="STA"))

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

                if competiton not in user.competition.all() and competiton.status == "STA":
                    user.competition.add(competiton)

            else:
                if competiton in user.competition.all() and competiton.status == "STA":
                    score = int(data['score'])
                    user.score += score
                    user.save()
            
            return Response({},status=status.HTTP_200_OK)
            

def decodeToken(token):
    token = jwt.decode(token, GAME_SECRET_KEY, algorithm=GAME_ALGORITHM)
    return GameProfile.objects.get(nickname=token['nickname'])
