import re
import requests
import os
import zipfile

from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Q

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated  # 로그인 인증토큰
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import permission_classes, authentication_classes

from .models import (
    Game,
    Comment,
    Screenshot,
    Star,
    Tag,
    Star,
)
from .serializers import (
    GameListSerializer,
    GameDetailSerializer,
    CommentSerializer,
    ScreenshotSerializer,
    TagSerailizer,
)

from django.conf import settings
from openai import OpenAI



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
        tag_q = request.query_params.get('tag-q')
        game_q = request.query_params.get('game-q')
        maker_q = request.query_params.get('maker-q')
        gm_q = request.query_params.get('gm-q')
        order = request.query_params.get('order')
        search = request.query_params.get('search')
        
        if tag_q:
            rows = Tag.objects.get(name=tag_q).games.filter(is_visible=True, register_state=1)
        elif game_q:
            rows = Game.objects.filter(
                is_visible=True,
                register_state=1,
                title__icontains=game_q
            )
        elif maker_q:
            rows = Game.objects.filter(maker__username__icontains=maker_q).filter(is_visible=True, register_state=1)
        elif gm_q:
            rows = Game.objects.filter(
                Q(title__contains=gm_q) | Q(maker__username__icontains=gm_q)
            ).filter(is_visible=True, register_state=1)
        else:
            rows = Game.objects.filter(is_visible=True, register_state=1)

        rows = rows.annotate(star=Avg('stars__star'))

        if order == 'new':
            rows = rows.order_by('-created_at')
        elif order == 'view':
            rows = rows.order_by('-view_cnt')
        elif order == 'star':
            rows = rows.order_by('-star')
        else:
            rows = rows.order_by('-created_at')
        
        if search:
            paginator = PageNumberPagination()
            result=paginator.paginate_queryset(rows,request)
            serializer = GameListSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = GameListSerializer(rows, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

    """
    게임 등록
    """

    def post(self, request):
        # Game model에 우선 저장
        game = Game.objects.create(
            title=request.data.get('title'),
            thumbnail=request.FILES.get('thumbnail'),
            youtube_url=request.data.get('youtube_url'),
            maker=request.user,
            content=request.data.get('content'),
            gamefile=request.FILES.get('gamefile'),
        )

        # 태그 저장
        tag_data = request.data.get('tag')
        if tag_data:
            for item in tag_data.split(','):
                game.tag.add(Tag.objects.get(name=item))

        # 이후 Screenshot model에 저장
        screenshots = list()
        for item in request.FILES.getlist("screenshots"):
            screenshot=Screenshot.objects.create(
                src=item,
                game=game
            )
            screenshots.append(screenshot.src.url)

        # 확인용 response
        return Response(
            {
                "game": {
                    "title": game.title,
                },
                "screenshots": screenshots
            },
            status=status.HTTP_200_OK
        )


class GameDetailAPIView(APIView):
    """
    포스트일 때 로그인 인증을 위한 함수
    """

    def get_permissions(self):  # 로그인 인증토큰
        permissions = super().get_permissions()

        if self.request.method.lower() == ('put' or 'delete'):  # 포스트할때만 로그인
            permissions.append(IsAuthenticated())

        return permissions

    def get_object(self, game_pk):
        return get_object_or_404(Game, pk=game_pk, is_visible=True)

    """
    게임 상세 조회
    """

    def get(self, request, game_pk):
        game = self.get_object(game_pk)
        game.view_cnt += 1  # 아티클 뷰수 조회
        game.save()  # 아티클 뷰수 조회
        
        stars = list(game.stars.all().values('star'))
        star_list = [d['star'] for d in stars]
        if len(star_list) == 0:
            star_score = None
        else:
            star_score = round(sum(star_list)/len(star_list), 1)
        serializer = GameDetailSerializer(game)
        # data에 serializer.data를 깊은 복사함
        # serializer.data의 리턴값인 ReturnDict는 불변객체이다
        data = serializer.data

        screenshots = Screenshot.objects.filter(game_id=game_pk)
        screenshot_serializer = ScreenshotSerializer(screenshots, many=True)

        tags = game.tag.all()
        tag_serializer = TagSerailizer(tags, many=True)

        data["star_score"] = star_score
        data["screenshot"] = screenshot_serializer.data
        data['tag'] = tag_serializer.data

        return Response(data, status=status.HTTP_200_OK)

    """
    게임 수정
    """

    def put(self, request, game_pk):
        game = self.get_object(game_pk)
        if game.maker == request.user:
            if request.FILES.get("gamefile"):
                game.register_state=0
                game.gamefile = request.FILES.get("gamefile")
            game.title = request.data.get("title", game.title)
            game.thumbnail = request.FILES.get("thumbnail", game.thumbnail)
            game.youtube_url = request.data.get("youtube_url", game.youtube_url)
            game.content = request.data.get("content", game.content)
            game.save()

            tag_data = request.data.get('tag')
            if tag_data is not None:
                game.tag.clear()
                tags = [Tag.objects.get_or_create(name=item.strip())[0] for item in tag_data.split(',') if item.strip()]
                game.tag.set(tags)

            pre_screenshots_data = Screenshot.objects.filter(game=game)
            pre_screenshots_data.delete()

            if request.data.get('screenshots'):
                for item in request.FILES.getlist("screenshots"):
                    game.screenshots.create(src=item)

            return Response({"messege": "수정이 완료됐습니다"},status=status.HTTP_200_OK)
        else:
            return Response({"error": "작성자가 아닙니다"}, status=status.HTTP_400_BAD_REQUEST)

    """
    게임 삭제
    """

    def delete(self, request, game_pk):
        game = self.get_object(game_pk)
        if game.maker == request.user:
            game.is_visible = False
            game.save()
            return Response({"message": "삭제를 완료했습니다"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "작성자가 아닙니다"}, status=status.HTTP_400_BAD_REQUEST)


class GameLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_pk):
        game = get_object_or_404(Game, pk=game_pk)
        if game.like.filter(pk=request.user.pk).exists():
            game.like.remove(request.user)
            return Response({'message':"즐겨찾기 취소"}, status=status.HTTP_200_OK)
        else:
            game.like.add(request.user)
            return Response({'message':"즐겨찾기"}, status=status.HTTP_200_OK)


class GameStarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_pk):
        game = get_object_or_404(Game, pk=game_pk)
        if game.stars.filter(user=request.user).exists():
            # 수정
            game.stars.filter(user=request.user).update(
                star=request.data['star'])
        else:
            # 생성
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
        comments = Comment.objects.all().filter(game=game_pk,root__isnull=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self, request, game_pk):
        game = get_object_or_404(Game, pk=game_pk)  # game 객체를 올바르게 설정
        root_id = request.data.get('root')
        root = None
        if root_id:
            root = get_object_or_404(Comment, pk=root_id)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user, game=game, root=root)  # 데이터베이스에 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        if request.user == comment.author:
            serializer = CommentSerializer(
                comment, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "작성자가 아닙니다"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        if request.user == comment.author:
            comment.is_visible = False
            comment.content="삭제된 댓글입니다."
            comment.save()
            return Response({"message": "삭제를 완료했습니다"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "작성자가 아닙니다"}, status=status.HTTP_400_BAD_REQUEST)
        

class TagAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        tags=Tag.objects.all()
        serializer = TagSerailizer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TagSerailizer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return redirect("games:admin_tags")

    def delete(self, request):
        tag = get_object_or_404(Tag, pk=request.data['pk'])
        tag.delete()
        return Response({"message": "삭제를 완료했습니다"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def game_register(request, game_pk):
    # game_pk에 해당하는 row 가져오기 (게시 중인 상태이면서 '등록 중' 상태)
    row = get_object_or_404(
        Game, pk=game_pk, is_visible=True, register_state=0)

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
                new_lines += line[:cursor] + \
                    f'/media/games/{game_folder}/' + line[cursor:]
            elif line.find('buildUrl') > -1 and not is_check_build:
                is_check_build = True
                cursor = line.find('Build')
                new_lines += line[:cursor] + \
                    f'/media/games/{game_folder}/' + line[cursor:]
            else:
                new_lines += line

    # 덮어쓰기
    with open(f'{game_folder_path}/index.html', 'w') as f:
        f.write(new_lines)

    # index.html 외 다른 파일들 압축 해제
    zipfile.ZipFile(f"./{path}").extractall(
        path=game_folder_path,
        members=[item for item in zipfile.ZipFile(
            f"./{path}").namelist() if item != "index.html"]
    )

    # 게임 폴더 경로를 저장하고, 등록 상태 1로 변경(등록 성공)
    row.gamepath = game_folder_path[1:]
    row.register_state = 1
    row.save()

    # 알맞은 HTTP Response 리턴
    # return Response({"message": f"등록을 성공했습니다. (게시물 id: {game_pk})"}, status=status.HTTP_200_OK)
    return redirect("games:admin_list")

@api_view(['POST'])
def game_register_deny(request, game_pk):
    row = get_object_or_404(Game, pk=game_pk, is_visible=True, register_state=0)
    row.register_state = 2
    row.save()
    return redirect("games:admin_list")

@api_view(['POST'])
def game_dzip(request, game_pk):
    row = get_object_or_404(Game, pk=game_pk, register_state=0, is_visible=True)
    zip_path = row.gamefile.url
    zip_folder_path = "./media/zips/"
    zip_name = os.path.basename(zip_path)

    # FileSystemStorage 인스턴스 생성
    # zip_folder_path에 대해 FILE_UPLOAD_PERMISSIONS = 0o644 권한 설정
    # 파일을 어디서 가져오는지를 정하는 것으로 보면 됨
    # 디폴트 값: '/media/' 에서 가져옴
    fs = FileSystemStorage(zip_folder_path)

    # FileResponse 인스턴스 생성
    # FILE_UPLOAD_PERMISSIONS 권한을 가진 상태로 zip_folder_path 경로 내의 zip_name 파일에 'rb' 모드로 접근
    # content_type 으로 zip 파일임을 명시
    response = FileResponse(fs.open(zip_name, 'rb'), content_type='application/zip')

    # 'Content-Disposition' value 값(HTTP Response 헤더값)을 설정
    # 파일 이름을 zip_name 으로 다운로드 폴더에 받겠다는 뜻
    response['Content-Disposition'] = f'attachment; filename="{zip_name}"'

    # FileResponse 객체를 리턴
    return response

CLIENT=OpenAI(api_key=settings.OPEN_API_KEY)

#chatbot API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ChatbotAPIView(request):
    input_data=request.data.get('input_data') #이름변경해야함
    taglist=list(Tag.objects.values_list('name',flat=True))
    instructions=f"""
    내가 제한한 태그 목록 : {taglist} 여기서만 이야기를 해줘, 이외에는 말하지마
    받은 내용을 요약해서 내가 제한한 목록에서 제일 관련 있는 항목 한 개를 골라줘
    결과 형식은 다른 말은 없이 꾸미지도 말고 딱! '태그:'라는 형식으로만 작성해줘
    결과에 특수문자 붙이지마
    """
    completion=CLIENT.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": f"받은 내용: {input_data}"},
        ],
    )
    gpt_response=completion.choices[0].message.content
    print("📌📌",gpt_response)
    about_tag=gpt_response.split('태그:')[1]
    about_tag=re.sub('[-=+,#/\?:^.@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]', '', about_tag)
    about_tag=about_tag.strip()
    print("📌📌",about_tag)
    untaglist=['없음','']
    if about_tag in untaglist:
        about_tag='없음'
    return Response({"tag":about_tag},status=status.HTTP_200_OK)
    

# 게임 등록 Api 테스트용 페이지 렌더링
def game_detail_view(request, game_pk):
    return render(request, "games/game_detail.html", {'game_pk':game_pk})


# 테스트용 base.html 렌더링
def test_base_view(request):
    return render(request, "base.html")


# 테스트용 메인 페이지 렌더링
def test_main_view(request):
    return render(request, "games/test_main.html")


# 테스트용 검색 페이지 렌더링
def test_search_view(request):
    # 쿼리스트링을 그대로 가져다가 '게임 목록 api' 호출
    return render(request, "games/test_search.html")


# 게임 검수용 페이지 뷰
def admin_list(request):
    rows = Game.objects.filter(is_visible=True, register_state=0)
    return render(request, "games/admin_list.html", context={"rows":rows})


def admin_tag(request):
    tags=Tag.objects.all()
    return render(request, "games/admin_tags.html", context={"tags":tags})


def game_create_view(request):
    return render(request, "games/game_create.html")


def game_update_view(request, game_pk):
    return render(request,"games/game_update.html",{'game_pk':game_pk})

def chatbot_view(request):
    return render(request,"games/chatbot.html")