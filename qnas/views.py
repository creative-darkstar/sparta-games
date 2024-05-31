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
    CategorySerializer
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
    QnA 목록 조회
    """
    def get(self, request):
        qnas = QnA.objects.all().filter(is_visible=True)
        serializer = QnAPostListSerializer(qnas, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    """
    QnA 등록
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
        return get_object_or_404(QnA, pk=qna_pk,is_visible=True)

    """
    QnA 상세 조회
    """
    def get(self, request, qna_pk):
        qna=self.get_object(qna_pk)
        serializer = QnAPostListSerializer(qna)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    """
    QnA 수정
    """
    def put(self, request, qna_pk):
        qna=self.get_object(qna_pk)
        serializer = QnAPostListSerializer(
            qna, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    """
    QnA 삭제
    """
    def delete(self, request, qna_pk):
        qna=self.get_object(qna_pk)
        qna.is_visible = False
        qna.save()
        return Response({"message":"삭제를 완료했습니다"},status=status.HTTP_204_NO_CONTENT)
    

class CategoryListView(APIView):
    def get(self, request):
        categories = QnA.CATEGORY_CHOICES
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


def qna_main_view(request):
    return render(request, 'qnas/qna_main.html')

def qna_detail_view(request, qna_pk):
    return render(request, "qnas/qna_detail.html", {'qna_pk': qna_pk})

def qna_create_view(request):
    return render(request, "qnas/qna_create.html")