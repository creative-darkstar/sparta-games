import os

from django.conf import settings
from django.db import models
from django.utils import timezone


class Tag(models.Model):
    name=models.CharField(max_length=20, unique=True)


class Game(models.Model):
    # media 폴더에 업로드할 게임 zip 파일명 변경 및 위치 설정
    def upload_to_func(instance, filename):
        time_data = timezone.now().strftime("%Y%m%d%H%M%S%f")
        file_name = os.path.splitext(filename)[0]
        extension = os.path.splitext(filename)[-1].lower()
        return "".join(["zips/", time_data, '_', file_name, extension,])

    title = models.CharField(max_length=100)
    thumbnail = models.ImageField(
        upload_to="images/thumbnail/",
        blank=True,
        null=True,
    )
    youtube_url = models.URLField(blank=True, null=True)
    maker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="games"
    )
    content = models.TextField()
    like = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="games_like"
    )
    view_cnt = models.IntegerField(default=0)
    gamefile = models.FileField(
        upload_to=upload_to_func
    )
    gamepath = models.CharField(blank=True,null=True,max_length=511)
    register_state = models.IntegerField(default=0)
    tag = models.ManyToManyField(
        Tag, related_name="games",
        null=True,
    )
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    content=models.TextField()
    is_visible=models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="comments"
    )
    root=models.ForeignKey("self",null=True ,on_delete=models.CASCADE, related_name="reply")
    author=models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )

class Screenshot(models.Model):
    src=models.ImageField(
        upload_to="images/screenshot/",
        blank=True,
        null=True,
    )
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="screenshots"
    )


class Star(models.Model):
    star=models.IntegerField(null=True)
    user=models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stars"
    )
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="stars"
    )
