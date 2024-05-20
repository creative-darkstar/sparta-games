from rest_framework import serializers
from .models import QnA


class QnAPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = QnA
        fields = "__all__"