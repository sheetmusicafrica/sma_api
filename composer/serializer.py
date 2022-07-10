from django.contrib.auth.models import User

from rest_framework import serializers

from .models import *

import datetime

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from sheet_music_africa.settings import FLUTTER_WAVE_COUNTRIES


class CustomJWTSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        credentials = {
            'username': '',
            'password': attrs.get("password")
        }

        # This is answering the original question, but do whatever you need here.
        # For example in my case I had to check a different model that stores more user info
        # But in the end, you should obtain the username to continue.
        user_obj = User.objects.filter(email=attrs.get("username").lower()).first(
        ) or User.objects.filter(username=attrs.get("username")).first()

        if user_obj:
            credentials['username'] = user_obj.username

        return super().validate(credentials)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'username']


class songUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ComposerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    subscriber = serializers.SerializerMethodField()
    use_paypal = serializers.SerializerMethodField()

    class Meta:
        model = ComposerProfile
        fields = [
            'pic', 'discription', 'background_image',
            'facebook_link', 'twitter_link', 'youtube_link',
            'soundcloud_link', 'user', 'subscriber', "use_paypal"
        ]

    def get_use_paypal(self, obj):
        if obj.country.upper() in FLUTTER_WAVE_COUNTRIES:
            return False
        return True

    def get_subscriber(self, obj):
        current_composer = ComposerProfile.objects.get(user=obj.user)
        return FollowComposer.objects.filter(main_composer=current_composer).count()


class ComposerRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowComposer
        fields = "__all__"


class PaymentLogSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    class Meta:
        model = UserPaymentLog
        fields = ['log_type', 'price', 'date', 'currency']

    def get_date(self, obj):
        date = obj.date
        return "%s/%s/%s" % (date.day, date.month, date.year)
