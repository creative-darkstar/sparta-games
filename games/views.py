import zipfile

from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    Game,
    Comment,
    Screenshot,
    Tag,
    Star,
)
from .serializers import (
    GameListSerializer,
    GameDetailSerializer,
    CommentSerializer,
)
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
        # Game model에 우선 저장
        game = Game.objects.create(
            title=request.data.get('title'),
            thumbnail=request.data.get('thumbnail'),
            youtube_url=request.data.get('youtube_url'),
            maker=request.user,
            content=request.data.get('content'),
            gamefile=request.data.get('gamefile'),
        )

        # 태그 저장
        tag_data = request.data.get('tag')
        if tag_data:
            for item in tag_data.split(','):
                game.tag.add(Tag.objects.get(name=item))

        # 이후 Screenshot model에 저장
        screenshots = list()
        for item in request.data.getlist("screenshots"):
            Screenshot.objects.create(
                src=item,
                game=game
            )
            screenshots.append(item.name)

        # 확인용 response
        return Response(
            {
                "game": {
                    "title": game.title,
                },
                "screenshots": screenshots
             },
            status=status.HTTP_201_CREATED
        )


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
            title = request.data.get("title", game.title)
            thumbnail=request.data.get("thumbnail", game.thumbnail)
            youtube_url=request.data.get("youtube_url", game.youtube_url)
            content=request.data.get("content", game.content)
            gamefile=request.data.get("gamefile", game.gamefile)

            tag_data = request.data.get('tag')
            pre_tag_data = game.tag.all()
            for item in pre_tag_data:
                game.tag.remove(item)
            if tag_data:
                for item in tag_data.split(','):
                    game.tag.add(Tag.objects.get(name=item))
            
            pre_screenshots_data=Screenshot.objects.all().filter(game=game)
            pre_screenshots_data.delete()
            screenshots = list()
            for item in request.data.getlist("screenshots"):
                game.screenshots.create(
                    src=item,
                    game=game
                )
                screenshots.append(item.name)
            for item in game.screenshots.all():
                print(item)

            return Response({})
            # serializer = GameDetailSerializer(game, data=request.data,partial=True)
            # if serializer.is_valid(raise_exception=True):
            #     serializer.save(register_state=0)
            #     return Response(serializer.data, status=status.HTTP_200_OK)
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

class GameStarAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, game_pk):
        game=get_object_or_404(Game,pk=game_pk)
        if game.stars.filter(user=request.user).exists():
            #수정
            game.stars.filter(user=request.user).update(star=request.data['star'])
        else:
            #생성
            Star.objects.create(
                star=request.data['star'],
                user=request.user,
                game=game,
            )
        return Response({"ok"}, status=status.HTTP_200_OK)

class CommentAPIView(APIView):
    def get_permissions(self):  # 로그인 인증토큰
        permissions = super().get_permissions()

        if self.request.method.lower() == 'post':  # 포스트할때만 로그인
            permissions.append(IsAuthenticated())

        return permissions

    def get(self, request, game_pk):
        comments = Comment.objects.all().filter(game=game_pk,is_visible=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, game_pk):
        game = get_object_or_404(Game, pk=game_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user,game=game)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        if request.user == comment.author:
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error":"작성자가 아닙니다"},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        if request.user == comment.author:
            comment.is_visible=False
            comment.save()
            return Response({"message":"삭제를 완료했습니다"},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error":"작성자가 아닙니다"},status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def game_register(request, game_pk):
    # game_pk에 해당하는 row 가져오기 (게시 중인 상태이면서 '등록 중' 상태)
    row = get_object_or_404(Game, pk=game_pk, is_visible=True, register_state=0)

    # gamefile 필드에 저장한 경로값을 'path' 변수에 저장
    path = row.gamefile.url

    # ~/<업로드시각>_<압축파일명>.zip 에서 '<업로드시각>_<압축파일명>' 추출
    game_folder = path.split('/')[-1].split('.')[0]

    # 게임 폴더 경로(압축을 풀 경로): './media/games/<업로드시각>_<압축파일명>'
    game_folder_path = f"./media/games/{game_folder}"

    # index.html 우선 압축 해제
    zipfile.ZipFile(f"./{path}").extract("index.html", game_folder_path)

    """
    index.html 내용 수정
    <link> 태그 href 값 수정 (line: 7, 8)
    var buildUrl 변수 값 수정 (line: 59)
    
    new_lines: 덮어쓸 내용 저장
    is_check_build: Build 키워드 찾은 후 True로 변경 (이후 라인에서 Build 찾는 것을 피하기 위함)
    """

    new_lines = str()
    is_check_build = False

    # 덮어쓸 내용 담기
    with open(f"{game_folder_path}/index.html", 'r') as f:
        for line in f.readlines():
            if line.find('link') > -1:
                cursor = line.find('TemplateData')
                new_lines += line[:cursor] + f'/media/games/{game_folder}/' + line[cursor:]
            elif line.find('buildUrl') > -1 and not is_check_build:
                is_check_build = True
                cursor = line.find('Build')
                new_lines += line[:cursor] + f'/media/games/{game_folder}/' + line[cursor:]
            else:
                new_lines += line

    # 덮어쓰기
    with open(f'{game_folder_path}/index.html', 'w') as f:
        f.write(new_lines)

    # index.html 외 다른 파일들 압축 해제
    zipfile.ZipFile(f"./{path}").extractall(
        path=game_folder_path,
        members=[item for item in zipfile.ZipFile(f"./{path}").namelist() if item != "index.html"]
    )

    # 게임 폴더 경로를 저장하고, 등록 상태 1로 변경(등록 성공)
    row.gamepath = game_folder_path[1:]
    row.register_state = 1
    row.save()

    # 알맞은 HTTP Response 리턴
    return Response({"message": f"등록을 성공했습니다. (게시물 id: {game_pk})"}, status=status.HTTP_200_OK)


# 게임 등록 Api 테스트용 페이지 렌더링
def game_detail_view(request, game_pk):
    # game_pk에 해당하는 row 가져오기 (게시 중인 상태이면서 '등록 중' 상태)
    row = Game.objects.get(pk=game_pk, is_visible=True)

    # context에 폴더명 담아서 render
    return render(request, "games/game_detail.html", context={"gamepath": row.gamepath})
