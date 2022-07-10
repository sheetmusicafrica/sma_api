import random
import string

from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, generics, views, status

from . models import PasswordRestLink

from utility.email import send_reset_password_email

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def updatePassword(request):
    data = request.POST

    if 'token' in data.keys():
        password = data['password']
        confirm_password = data['confirm_password']

        user_token = PasswordRestLink.objects.get(token=data['token'])
        user = user_token.user
        if password == confirm_password:
            user.set_password(password)
            user.save()
            user_token.delete()
            return Response({'msg': 'successful'})

    return Response({'msg': 'failed'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def checkToken(request):
    msg = "invalid"
    token = request.POST['token']
    try:
        reset_token = PasswordRestLink.objects.get(token=token)
        if UserHasValidToken(reset_token.user) == True:
            msg = "valid"
    except PasswordRestLink.DoesNotExist:
        pass

    return Response({'msg': msg})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def generatePasswordToken(request):
    email = request.POST['email'].lower()
    try:
        user = User.objects.get(email=email)

        if UserHasValidToken(user) == True:
            # if user has generated token before delete old token
            PasswordRestLink.objects.get(user=user).delete()

        password_token = PasswordRestLink()
        password_token.user = user
        password_token.token = generateToken()
        password_token.save()

        send_reset_password_email(password_token.token,user.email)

    except User.DoesNotExist:
        pass

    return Response({'msg': 'done'})


def generateToken():
    # generate random string of length k=200
    return ''.join(random.choices(string.ascii_letters + string.digits, k=200))


def UserHasValidToken(user):
    try:
        user_token = PasswordRestLink.objects.get(user=user)
        token_lifespan = 10 * 60
        if (timezone.now() - user_token.date_created).seconds > token_lifespan:
            # token has expired
            user_token.delete()
            return False
        else:
            return True

    except PasswordRestLink.DoesNotExist:
        return False


def sendTokenToEmail(email, token):
    pass
