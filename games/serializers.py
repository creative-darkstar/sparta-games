from rest_framework import serializers
from .models import Game, Comment, Screenshot, Tag


class GameListSerializer(serializers.ModelSerializer):
    star = serializers.FloatField(read_only=True)
    maker_name = serializers.CharField(source='maker.username')

    class Meta:
        model = Game
        fields = ("pk", "title", "maker", "thumbnail",
                  "star", "maker_name", "view_cnt")


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
    author_name = serializers.CharField(
        source='author.username', read_only=True)
    src = serializers.ImageField(source='author.image', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ('is_visible', 'game', 'author',)

    def get_replies(self, obj):
        if obj.reply.exists():
            return CommentSerializer(obj.reply, many=True).data
        return []


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = ('id', 'src', )


class TagSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('pk', 'name')
