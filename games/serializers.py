from rest_framework import serializers
from .models import Game


class GameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ("thumbnail","title","maker",)
