from django.db import models

# Create your models here.
class QnA(models.Model):
    CATEGORY_CHOICES = (
        ("U", "계정 문의"),
        ("E", "게임 실행 문의"),
        ("R", "게임 등록 문의"),
    )
    title=models.CharField(max_length=100)
    content=models.TextField()
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)