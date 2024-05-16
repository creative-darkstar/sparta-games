from django.conf import settings
from django.db import models


class Tag(models.Model):
    name=models.CharField(max_length=20)


class Game(models.Model):
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
        upload_to="zips/"
    )
    gamepath = models.CharField(blank=True,null=True,max_length=511)
    register_state = models.IntegerField(default=0)
    tag = models.ManyToManyField(
        Tag, related_name="games"
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
    root=models.ForeignKey("self", on_delete=models.CASCADE, related_name="reply")
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
