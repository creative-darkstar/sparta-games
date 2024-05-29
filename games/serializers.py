from rest_framework import serializers
from .models import Game, Comment, Screenshot, Tag


class GameListSerializer(serializers.ModelSerializer):
    star = serializers.FloatField(read_only=True)

    class Meta:
        model = Game
        fields = ("pk", "title", "maker", "thumbnail", "star")


class GameCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"
        read_only_fields = ('like', 'tag', 'maker',
                            'is_visible', 'view_cnt', 'register_state')


class GameDetailSerializer(serializers.ModelSerializer):
    maker_name = serializers.CharField(source='maker.username')
    class Meta:
        model = Game
        fields = "__all__"
        read_only_fields = ('like', 'tag', 'maker')


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username')
    src = serializers.ImageField(source='author.image')

    # def to_representation(self, instance):
    #     ret = super().to_representation(instance)
    #     src = ret.pop("src")
    #     ret["src"] = src.url if src else '/image/user.png/'
    #     return ret
    
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ('is_visible', 'game', 'author',)
    


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = ('id', 'src', )


class TagSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('pk','name')