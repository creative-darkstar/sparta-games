import zipfile

from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    QnA,
)
from .serializers import (
    QnAPostListSerializer,
)
from rest_framework.permissions import IsAuthenticated  # 로그인 인증토큰
from rest_framework import status


class QnAPostListAPIView(APIView):
    """
    포스트일 때 로그인 인증을 위한 함수
    """
    def get_permissions(self):  # 로그인 인증토큰
        permissions = super().get_permissions()

        if self.request.method.lower() == 'post':  # 포스트할때만 로그인
            permissions.append(IsAuthenticated())

        return permissions
    
    """
    게임 목록 조회
    """
    def get(self, request):
        qnas = QnA.objects.all()
        serializer = QnAPostListSerializer(qnas, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    """
    게임 등록
    """
    def post(self, request):
        serializer = QnAPostListSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class QnADetailAPIView(APIView):
    """
    포스트일 때 로그인 인증을 위한 함수
    """
    def get_permissions(self):  # 로그인 인증토큰
        permissions = super().get_permissions()

        if self.request.method.lower() == ('put'or'delete'):  # 포스트할때만 로그인
            permissions.append(IsAuthenticated())

        return permissions
    
    def get_object(self, qna_pk):
        return get_object_or_404(QnA, pk=qna_pk)

    """
    게임 상세 조회
    """
    def get(self, request, qna_pk):
        qna=self.get_object(qna_pk)
        serializer = QnAPostListSerializer(qna)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    """
    게임 수정
    """
    def put(self, request, qna_pk):
        qna=self.get_object(qna_pk)
        serializer = QnAPostListSerializer(
            qna, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    """
    게임 삭제
    """
    def delete(self, request, qna_pk):
        qna=self.get_object(qna_pk)
        qna.delete()
        return Response({"message":"삭제를 완료했습니다"},status=status.HTTP_204_NO_CONTENT)
