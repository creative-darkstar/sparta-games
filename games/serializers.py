from rest_framework import serializers
from .models import Game,Comment,Star
from django.db.models import Avg

class GameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("pk","title","maker" , "thumbnail",)


class GameCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"
        read_only_fields = ('like', 'tag', 'maker','is_visible','view_cnt','register_state')


class GameDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"
        read_only_fields = ('like', 'tag', 'maker')

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields = "__all__"
        read_only_fields = ('is_visible', 'game', 'author',)
