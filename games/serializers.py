from rest_framework import serializers
from .models import Game


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
    # screenshot
    class Meta:
        model = Game
        fields = "__all__"
        read_only_fields = ('like', 'tag', 'maker')
