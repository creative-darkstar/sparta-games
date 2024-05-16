from django.shortcuts import render,get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Game, Comment
from .serializers import GameListSerializer, GameCreateSerializer,GameDetailSerializer,CommentSerializer
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
        games = Game.objects.filter(is_visible=True)
        serializer = GameListSerializer(games, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    """
    게임 등록
    """
    def post(self, request):
        serializer = GameCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(maker=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class GameDetailAPIView(APIView):
    """
    포스트일 때 로그인 인증을 위한 함수
    """
    def get_permissions(self):  # 로그인 인증토큰
        permissions = super().get_permissions()

        if self.request.method.lower() == ('put'or'delete'):  # 포스트할때만 로그인
            permissions.append(IsAuthenticated())

        return permissions
    
    def get_object(self, game_pk):
        return get_object_or_404(Game, pk=game_pk, is_visible=True)

    """
    게임 상세 조회
    """
    def get(self, request, game_pk):
        game=self.get_object(game_pk)
        game.view_cnt += 1  # 아티클 뷰수 조회
        game.save()  # 아티클 뷰수 조회
        serializer = GameDetailSerializer(game)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    """
    게임 수정
    """
    def put(self, request, game_pk):
        game = self.get_object(game_pk)
        if game.maker == request.user:
            serializer = GameDetailSerializer(game, data=request.data,partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error":"작성자가 아닙니다"},status=status.HTTP_400_BAD_REQUEST)

    """
    게임 삭제
    """
    def delete(self, request, game_pk):
        game = self.get_object(game_pk)
        if game.maker == request.user:
            game.is_visible=False
            game.save()
            return Response({"message":"삭제를 완료했습니다"},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error":"작성자가 아닙니다"},status=status.HTTP_400_BAD_REQUEST)

class GameLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_pk):
        game=get_object_or_404(Game,pk=game_pk)
        if game.like.filter(pk=request.user.pk).exists():
            game.like.remove(request.user)
            return Response("안좋아요", status=status.HTTP_200_OK)
        else:
            game.like.add(request.user)
            return Response("좋아요", status=status.HTTP_200_OK)

class CommentAPIView(APIView):
    def get_permissions(self):  # 로그인 인증토큰
        permissions = super().get_permissions()

        if self.request.method.lower() == 'post':  # 포스트할때만 로그인
            permissions.append(IsAuthenticated())

        return permissions

    def get(self, request, game_pk):
        comments = Comment.objects.all().filter(game=game_pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, game_pk):
        game = get_object_or_404(Game, pk=game_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user,game=game)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailAPIView(APIView):
    pass
    # permission_classes = [IsAuthenticated]
    # def put(self, request, pk, comment_id):
    #     comment = get_object_or_404(Comment, pk=comment_id)
    #     if request.user == comment.user:
    #         serializer = CommentSerializer(comment, data=request.data, partial=True)
    #         print(serializer)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     return Response(status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk, comment_id):
    #     comment = get_object_or_404(Comment, pk=comment_id)
    #     if request.user == comment.user:
    #         comment.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     return Response(status=status.HTTP_400_BAD_REQUEST)