from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Game
from .serializers import GameListSerializer, GameCreateSerializer
from rest_framework.permissions import IsAuthenticated  # 로그인 인증토큰
from rest_framework import status

class GameListAPIView(APIView):
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
        games = Game.objects.all()
        serializer = GameListSerializer(games, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    """
    게임 등록
    """
    def post(self, request):
        # request.data["username"] = request.user.username
        serializer = GameCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(maker=request.user.username)
            return Response(serializer.data, status=status.HTTP_201_CREATED)