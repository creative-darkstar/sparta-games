from rest_framework import serializers
from .models import Game


class GameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("thumbnail","title","maker",)

class GameCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Game
        fields="__all__"
        readonly_fields =('like','tag')

class GameDetailSerializer(serializers.ModelSerializer):
    # screenshot
    class Meta:
        model=Game
        fields="__all__"