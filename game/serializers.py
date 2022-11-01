from rest_framework import serializers

from .models import Competition, GameProfile,ScoreLog


class GameProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = GameProfile
        fields = ["full_name",'nickname', "pic", "score","email","state","password"]


class LeaderBoardSerializer(serializers.ModelSerializer):

    high_score = serializers.SerializerMethodField()

    class Meta:
        model = GameProfile
        fields = ["full_name","pic", "score","high_score","email"]   
 

    def get_high_score(self, obj):
        scores = ScoreLog.objects.filter(profile=obj).order_by("-score")
        if scores.count() == 0:
            return 0

        return scores[0].score


class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = GameProfile
        fields = ["full_name",'nickname', "pic","email","state"]


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ["id","name","location","status"]
                  