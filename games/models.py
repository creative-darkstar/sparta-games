from django.conf import settings
from django.db import models


class Tag(models.Model):
    pass


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
        settings.AUTH_USER_MODEL, related_name="games"
    )
    view_cnt = models.IntegerField(default=0)
    gamefile = models.FileField(
        upload_to="zips/"
    )
    gamepath = models.FileField(
        upload_to="games/"
    )
    register_state = models.IntegerField(default=0)
    tag = models.ManyToManyField(
        Tag, related_name="games"
    )
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    pass


class Screenshot(models.Model):
    pass


class Star(models.Model):
    pass
