from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    image = models.ImageField(
        upload_to="images/profile/",
        blank=True,
        null=True,
    )
