from rest_framework import serializers
from .models import QnA


class QnAPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = QnA
        fields = "__all__"


class CategorySerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()

    def to_representation(self, instance):
        return {
            'code': instance[0],
            'name': instance[1]
        }
