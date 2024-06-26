import io
import re
import os
import zipfile

import boto3

from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Q
from django.db.models.functions import Round

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated  # 로그인 인증토큰
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import permission_classes

from .models import (
    Game,
    Comment,
    Screenshot,
    Star,
    Tag,
    Star,
)
from accounts.models import BotCnt
from .serializers import (
    GameListSerializer,
    GameDetailSerializer,
    CommentSerializer,
    ScreenshotSerializer,
    TagSerailizer,
)
from spartagames import config
from django.conf import settings

from django.conf import settings
from openai import OpenAI
from django.utils import timezone


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

        # 검색옵션 별 목록화
        if tag_q:
            rows = Game.objects.filter(tag__name__icontains=tag_q).filter(
                is_visible=True, register_state=1)
        elif game_q:
            rows = Game.objects.filter(
                is_visible=True,
                register_state=1,
                title__icontains=game_q
            )
        elif maker_q:
            rows = Game.objects.filter(maker__username__icontains=maker_q).filter(
                is_visible=True, register_state=1)
        elif gm_q:
            rows = Game.objects.filter(
                Q(title__contains=gm_q) | Q(maker__username__icontains=gm_q)
            ).filter(is_visible=True, register_state=1)
        else:
            rows = Game.objects.filter(is_visible=True, register_state=1)

        rows = rows.annotate(star=Round(Avg('stars__star'), 1))

        # 추가 옵션 정렬
        if order == 'new':
            rows = rows.order_by('-created_at')
        elif order == 'view':
            rows = rows.order_by('-view_cnt')
        elif order == 'star':
            rows = rows.order_by('-star')
        else:
            rows = rows.order_by('-created_at')

        # search_pagination
        if search:
            paginator = PageNumberPagination()
            result = paginator.paginate_queryset(rows, request)
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
            screenshot = Screenshot.objects.create(
                src=item,
                game=game
            )
            screenshots.append(screenshot.src.url)

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
        # data에 serializer.data를 assignment
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
        
        # 작성한 유저이거나 관리자일 경우 동작함
        if game.maker == request.user or request.user.is_staff == True:
            if request.FILES.get("gamefile"): # 게임파일을 교체할 경우 검수페이지로 이동
                game.register_state = 0
                game.gamefile = request.FILES.get("gamefile")
            game.title = request.data.get("title", game.title)
            game.thumbnail = request.FILES.get("thumbnail", '')
            game.youtube_url = request.data.get(
                "youtube_url", game.youtube_url)
            game.content = request.data.get("content", game.content)
            game.save()

            tag_data = request.data.get('tag')
            if tag_data is not None: # 태그가 바뀔 경우 기존 태그를 초기화, 신규 태그로 교체
                game.tag.clear()
                tags = [Tag.objects.get_or_create(name=item.strip())[
                    0] for item in tag_data.split(',') if item.strip()]
                game.tag.set(tags)

            # 기존 데이터 삭제
            pre_screenshots_data = Screenshot.objects.filter(game=game)
            pre_screenshots_data.delete()

            # 받아온 스크린샷으로 교체
            if request.data.get('screenshots'): 
                for item in request.FILES.getlist("screenshots"):
                    game.screenshots.create(src=item)

            return Response({"messege": "수정이 완료됐습니다"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "작성자가 아닙니다"}, status=status.HTTP_400_BAD_REQUEST)

    """
    게임 삭제
    """

    def delete(self, request, game_pk):
        game = self.get_object(game_pk)

        # 작성한 유저이거나 관리자일 경우 동작함
        if game.maker == request.user or request.user.is_staff == True:
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
            # 수정
            game.like.remove(request.user)
            return Response({'message': "즐겨찾기 취소"}, status=status.HTTP_200_OK)
        else:
            # 생성
            game.like.add(request.user)
            return Response({'message': "즐겨찾기"}, status=status.HTTP_200_OK)


class GameStarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_pk):
        star_list = [1,2,3,4,5]
        star = int(request.data['star'])
        if star not in star_list:
            star = 5
        game = get_object_or_404(Game, pk=game_pk)
        if game.stars.filter(user=request.user).exists():
            # 수정
            game.stars.filter(user=request.user).update(
                star=star)
        else:
            # 생성
            Star.objects.create(
                star=star,
                user=request.user,
                game=game,
            )
        star_values=[item['star'] for item in game.stars.values()]
        average_star = round(sum(star_values) / len(star_values),1)
        return Response({"res":"ok","avg_star":average_star}, status=status.HTTP_200_OK)


class CommentAPIView(APIView):
    def get_permissions(self):  # 로그인 인증토큰
        permissions = super().get_permissions()

        if self.request.method.lower() == 'post':  # 포스트할때만 로그인
            permissions.append(IsAuthenticated())

        return permissions

    def get(self, request, game_pk):
        comments = Comment.objects.all().filter(game=game_pk, root__isnull=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, game_pk):
        game = get_object_or_404(Game, pk=game_pk)  # game 객체를 올바르게 설정
        
        # root 기본 설정
        root_id = request.data.get('root')
        root = None

        # root_id가 있으면 대댓글의 root를 설정
        if root_id:
            root = get_object_or_404(Comment, pk=root_id)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user, game=game,
                            root=root)  # 데이터베이스에 저장(root가 none이면 댓글, 값이 있으면 대댓글)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)

        # 작성한 유저이거나 관리자일 경우 동작함
        if request.user == comment.author or request.user.is_staff == True:
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

        # 작성한 유저이거나 관리자일 경우 동작함
        if request.user == comment.author or request.user.is_staff == True:
            comment.is_visible = False
            comment.content = "삭제된 댓글입니다."
            comment.save()
            return Response({"message": "삭제를 완료했습니다"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "작성자가 아닙니다"}, status=status.HTTP_400_BAD_REQUEST)


class TagAPIView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerailizer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.is_staff is False:
            return Response({"error": "권한이 없습니다"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TagSerailizer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "태그를 추가했습니다"}, status=status.HTTP_200_OK)

    def delete(self, request):
        if request.user.is_staff is False:
            return Response({"error": "권한이 없습니다"}, status=status.HTTP_400_BAD_REQUEST)
        tag = get_object_or_404(Tag, pk=request.data['pk'])
        tag.delete()
        return Response({"message": "삭제를 완료했습니다"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def game_register(request, game_pk):
    # game_pk에 해당하는 row 가져오기 (게시 중인 상태이면서 '등록 중' 상태)
    row = get_object_or_404(
        Game, pk=game_pk, is_visible=True, register_state=0)

    # gamefile 필드에 저장한 경로값을 'path' 변수에 저장
    path = "media/" + row.gamefile.name

    # ~/<업로드시각>_<압축파일명>.zip 에서 '<업로드시각>_<압축파일명>' 추출
    game_folder = path.split('/')[-1].split('.')[0]

    s3 = boto3.client(
        's3',
        aws_access_key_id=config.AWS_AUTH["aws_access_key_id"],
        aws_secret_access_key=config.AWS_AUTH["aws_secret_access_key"],
        region_name='ap-northeast-2'
    )

    # S3에서 zip 파일을 읽어옴
    zip_resp = s3.get_object(Bucket=config.AWS_S3_BUCKET_NAME, Key=path)

    # BytesIO를 사용하여 메모리에 파일 데이터를 읽음
    zip_data = io.BytesIO(zip_resp['Body'].read())

    zip_ref = zipfile.ZipFile(zip_data)

    # index.html 내용 수정
    # <link> 태그 href 값 수정 (line: 7, 8)
    # var buildUrl 변수 값 수정 (line: 59)

    # new_lines: 덮어쓸 내용 저장
    # is_check_build: Build 키워드 찾은 후 True로 변경 (이후 라인에서 Build 찾는 것을 피하기 위함)

    new_lines = str()
    is_check_build = False

    index_text = zip_ref.read('index.html').decode('utf-8')
    for line in index_text.splitlines():
        if line.find('link') > -1:
            cursor = line.find('TemplateData')
            new_lines += line[:cursor] + f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/games/{game_folder}/' + line[cursor:]
        elif line.find('buildUrl') > -1 and not is_check_build:
            is_check_build = True
            cursor = line.find('Build')
            new_lines += line[:cursor] + f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/games/{game_folder}/' + line[cursor:]
        else:
            new_lines += line
        new_lines += '\n'

    # 추가할 JavaScript 코드
    additional_script = """
    <script>
      function sendSizeToParent() {
        var canvas = document.querySelector("#unity-canvas");
        var width = canvas.clientWidth;
        var height = canvas.clientHeight;
        window.parent.postMessage({ width: width, height: height }, '*');
      }

      window.addEventListener('resize', sendSizeToParent);
      window.addEventListener('load', sendSizeToParent);
    </script>
    """
    # CSS 스타일 추가 (body 태그와 unity-container에 overflow: hidden 추가)
    new_lines = new_lines.replace('<body',
                                  '<body style="margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden;"')
    new_lines = new_lines.replace('<div id="unity-container"',
                                  '<div id="unity-container" style="width: 100%; height: 100%; overflow: hidden;"')

    # </body> 태그 전에 추가할 스크립트 삽입
    body_close_tag_index = new_lines.find('</body>')
    new_lines = new_lines[:body_close_tag_index] + additional_script + new_lines[body_close_tag_index:]

    new_zip_data = io.BytesIO()
    with zipfile.ZipFile(new_zip_data, 'w') as new_zip_ref:
        for item in zip_ref.infolist():
            if item.filename != 'index.html':
                new_zip_ref.writestr(item, zip_ref.read(item.filename))
        new_zip_ref.writestr('index.html', new_lines.encode('utf-8'))

        for file_name in new_zip_ref.namelist():
            pattern1 = r".+\.(data|symbols\.json)\.gz$"
            pattern2 = r".+\.js\.gz$"
            pattern3 = r".+\.wasm\.gz$"
            file_extension = file_name.split('.')[-1].lower()

            content_type = None
            content_encoding = None

            # 메타데이터 설정
            metadata = {}
            if re.match(pattern1, file_name):
                content_type = 'application/octet-stream'
                content_encoding = 'gzip'
            elif re.match(pattern2, file_name):
                content_type = 'application/javascript'
                content_encoding = 'gzip'
            elif re.match(pattern3, file_name):
                content_type = 'application/wasm'
                content_encoding = 'gzip'
            else:
                if file_extension == "js":
                    content_type = 'application/javascript'
                elif file_extension == "html":
                    content_type = 'text/html'
                elif file_extension == "ico":
                    content_type = 'image/x-icon'
                elif file_extension == "png":
                    content_type = 'image/png'
                elif file_extension == "css":
                    content_type = 'text/css'

            response = s3.put_object(
                Body=new_zip_ref.open(file_name),
                Bucket=config.AWS_S3_BUCKET_NAME,
                Key=f"media/games/{game_folder}/{file_name}",
                ContentType=(content_type if content_type else 'text/plain'),
                ContentEncoding=(content_encoding if content_encoding else 'identity')
            )

    zip_ref.close()

    # 게임 폴더 경로를 저장하고, 등록 상태 1로 변경(등록 성공)
    row.gamepath = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/games/{game_folder}'
    row.register_state = 1
    row.save()

    # 알맞은 HTTP Response 리턴
    # return Response({"message": f"등록을 성공했습니다. (게시물 id: {game_pk})"}, status=status.HTTP_200_OK)
    return redirect("games:admin_list")


@api_view(['POST'])
def game_register_deny(request, game_pk):
    row = get_object_or_404(
        Game, pk=game_pk, is_visible=True, register_state=0)
    row.register_state = 2
    row.save()
    return redirect("games:admin_list")


@api_view(['POST'])
def game_dzip(request, game_pk):
    row = get_object_or_404(Game, pk=game_pk, register_state=0, is_visible=True)
    zip_path = "media/" + row.gamefile.name
    zip_name = os.path.basename(zip_path)
    s3_client = boto3.client(
        's3',
        aws_access_key_id=config.AWS_AUTH["aws_access_key_id"],
        aws_secret_access_key=config.AWS_AUTH["aws_secret_access_key"],
        region_name='ap-northeast-2'
    )
    s3_response = s3_client.get_object(Bucket=config.AWS_S3_BUCKET_NAME, Key=zip_path)
    file_stream = s3_response['Body'].read()

    # 메모리 스트림을 FileResponse로 반환
    response = FileResponse(io.BytesIO(file_stream), content_type='application/zip')

    # 'Content-Disposition' value 값(HTTP Response 헤더값)을 설정
    # 파일 이름을 zip_name 으로 다운로드 폴더에 받겠다는 뜻
    response['Content-Disposition'] = f'attachment; filename="{zip_name}"'

    # FileResponse 객체를 리턴
    return response


CLIENT = OpenAI(api_key=settings.OPEN_API_KEY)
MAX_USES_PER_DAY = 10 # 하루 당 질문 10개로 제한기준

# chatbot API


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ChatbotAPIView(request):
    user = request.user
    today = timezone.now().date()

    usage, created = BotCnt.objects.get_or_create(user=user, date=today)

    if usage.count >= MAX_USES_PER_DAY:
        return Response({"error": "Daily usage limit reached"}, status=status.HTTP_400_BAD_REQUEST)

    usage.count += 1
    usage.save()

    input_data = request.data.get('input_data')
    taglist = list(Tag.objects.values_list('name', flat=True))
    
    # GPT API와 통신을 통해 답장을 받아온다.(아래 형식을 따라야함)(추가 옵션은 문서를 참고)
    instructions = f"""
    내가 제한한 태그 목록 : {taglist} 여기서만 이야기를 해줘, 이외에는 말하지마
    받은 내용을 요약해서 내가 제한한 목록에서 제일 관련 있는 항목 한 개를 골라줘
    결과 형식은 다른 말은 없이 꾸미지도 말고 딱! '태그:'라는 형식으로만 작성해줘
    결과에 특수문자, 이모티콘 붙이지마
    """
    completion = CLIENT.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": f"받은 내용: {input_data}"},
        ],
    )

    # 응답받은 데이터 처리
    gpt_response = completion.choices[0].message.content
    about_tag = gpt_response.split('태그:')[1]
    about_tag = re.sub(
        '[-=+,#/\?:^.@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]', '', about_tag)
    about_tag = about_tag.strip()
    untaglist = ['없음', '']
    if about_tag in untaglist:
        about_tag = '없음'
    return Response({"tag": about_tag}, status=status.HTTP_200_OK)


# ---------- Web ---------- #


# 게임 등록 Api 테스트용 페이지 렌더링
def game_detail_view(request, game_pk):
    return render(request, "games/game_detail.html", {'game_pk': game_pk})


# 테스트용 base.html 렌더링
def test_base_view(request):
    return render(request, "base.html")


# 테스트용 메인 페이지 렌더링
def main_view(request):
    return render(request, "games/main.html")


# 테스트용 검색 페이지 렌더링
def search_view(request):
    # 쿼리스트링을 그대로 가져다가 '게임 목록 api' 호출
    return render(request, "games/search.html")


# 게임 검수용 페이지 뷰
def admin_list(request):
    rows = Game.objects.filter(is_visible=True, register_state=0)
    return render(request, "games/admin_list.html", context={"rows": rows})


def admin_tag(request):
    tags = Tag.objects.all()
    return render(request, "games/admin_tags.html", context={"tags": tags})


def game_create_view(request):
    return render(request, "games/game_create.html")


def game_update_view(request, game_pk):
    return render(request, "games/game_update.html", {'game_pk': game_pk})


def chatbot_view(request):
    return render(request, "games/chatbot.html")
