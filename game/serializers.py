from rest_framework import serializers

from .models import Competition, GameProfile


class GameProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = GameProfile
        fields = ["full_name",'nickname', "pic", "score","email","state","password"]


class LeaderBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameProfile
        fields = ["full_name","pic", "score","high_score","email"]   
 


class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = GameProfile
        fields = ["full_name",'nickname', "pic","email","state"]


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ["id","name","location","status"]
                  