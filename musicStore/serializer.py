from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import serializers
from .models import *

from composer.serializer import songUserSerializer
from composer.models import ComposerProfile, FollowComposer


class GenreSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ['id', 'name', 'is_instrument', 'background_image', 'count']

    def get_count(self, obj):
        return SheetMusic.objects.filter(Q(genre=obj) & Q(deleted=False) & Q(verified=True)).count()


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['id', 'name', 'price', 'main_song']


class OriginalSheetMusicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SheetMusic
        fields = "__all__"

from rest_framework.response import Response
class SheetMusicSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    composer = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    partScore = serializers.SerializerMethodField()


    class Meta:
        model = SheetMusic
        fields = ["id", "name", "genre", "discription", "rating", "skill_level", "video_link",
                  "demo", "thumbnail", "audio", "composer", "username", 'star', 'price', 'partScore']
                  

    def get_username(self, obj):
        return obj.composer.username

        

    def get_price(self, obj):
        return Score.objects.get(Q(main_song=obj) & Q(name="full_score")).price

    def get_composer(self, obj):
        composer = obj.composer
        return "%s %s" % (composer.first_name, composer.last_name)

    def get_partScore(self, obj):
        all_score = Score.objects.filter(Q(main_song=obj) & Q(deleted=False))
        try:
            if all_score.count() != 0:
                return ScoreSerializer(all_score, many=True).data
        except Score.DoesNotExist:
            pass
        return None


class SheetMusicOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score_sale
        fields = ['score', 'id']  # ,'user'


class CartSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    composer = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    cart_id = serializers.SerializerMethodField()

    class Meta:
        model = Score_sale
        fields = ['id', 'cart_id',
                  'price', 'composer', 'thumbnail', 'tags', 'name']

    def get_id(self, obj):
        return obj.score.id

    def get_cart_id(self, obj):
        return obj.id

    def get_name(self, obj):
        return obj.score.main_song.name

    def get_price(self, obj):
        return obj.score.price


    def get_tags(self, obj):
        song_tag = [tag.name for tag in obj.score.main_song.genre.all()]
        all_tag = ""
        for tag in song_tag:
            if song_tag.index(tag) == len(song_tag)-1:
                all_tag += tag
            else:
                all_tag += '%s, ' % tag
        return all_tag

    def get_thumbnail(self, obj):
        try:
            thumbnail = obj.score.main_song.thumbnail.url
        except:
            thumbnail = ""
        return thumbnail

    def get_composer(self, obj):
        composer = obj.score.main_song.composer
        return "%s %s" % (composer.first_name, composer.last_name)



class SheetMusicReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = My_review
        fields = ['rating', 'sheet', 'user']


class SheetSaleSerializer(serializers.ModelSerializer):
    sale_breakdown = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = SheetMusic
        fields = ['name', 'sale_breakdown',
                  'percentage', 'price', 'id', 'status']

    def get_status(self,obj):
    
        if obj.verified == True:
            return "approved"

        elif obj.rejected == True:
            return "rejected"  
        else:
            return "pending"

    def get_price(self, obj):
        return Score.objects.get(Q(main_song=obj) & Q(name="full_score")).price

    def get_percentage(self, obj):
        return obj.percentage

    def get_sale_breakdown(self, obj):
        sales_info = []

        for score in Score.objects.filter(main_song=obj):
            try:
                all_score_sale = Score_sale.objects.filter(
                    Q(score=score) & Q(purchased=True))
                total_price = sum(
                    [sale.purchased_price for sale in all_score_sale])

                if total_price > 0:
                    sales_info.append(
                        {'name': score.name, 'count': all_score_sale.count(), 'total_price': total_price})
            except Score_sale.DoesNotExist:
                pass

        return sales_info
