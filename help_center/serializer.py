from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = "__all__"

    def get_category(self,obj):
        return obj.category.name

