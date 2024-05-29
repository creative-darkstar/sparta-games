from django.http import JsonResponse
from django.shortcuts import redirect, render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import re
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginAPIView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = get_user_model().objects.filter(username=username).first()

        if not user:
            return Response({"message": "존재하지 않는 아이디입니다."},status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"message": "잘못된 비밀번호입니다. 다시 확인해주세요."},status=status.HTTP_400_BAD_REQUEST)

        token = TokenObtainPairSerializer.get_token(user)

        refresh_token = str(token)
        access_token = str(token.access_token)

        response = Response(
            {
                'user': {
                    'pk': user.pk,
                    'username': user.username,
                    'image': user.image.url if user.image else '/image/user.png/',
                },
                "jwt_token": {
                    "refresh": refresh_token,
                    "access": access_token,
                },
            },
            status=status.HTTP_200_OK
        )

        # response.set_cookie("access_token", access_token, httponly=True)
        # response.set_cookie("refresh_token", refresh_token, httponly=True)

        return response


class SignUpAPIView(APIView):
    # 유효성 검사 정규식 패턴
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{4,20}$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    PASSWORD_PATTERN = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,32}$')

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        password_check = request.data.get("password_check")
        email = request.data.get("email")

        # username 유효성 검사
        if not self.USERNAME_PATTERN.match(username):
            return Response({"error_message":"올바른 username을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        elif get_user_model().objects.filter(username=username).exists():
            return Response({"error_message":"이미 존재하는 username입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # password 유효성 검사
        if not self.PASSWORD_PATTERN.match(password):
            return Response({"error_message":"올바른 password.password_check를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        elif not password == password_check:
            return Response({"error_message":"암호를 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # email 유효성 검사
        if not self.EMAIL_PATTERN.match(email):
            return Response({"error_message":"올바른 email을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        elif get_user_model().objects.filter(email=email).exists():
            return Response({"error_message":"이미 존재하는 email입니다.."}, status=status.HTTP_400_BAD_REQUEST)
        

        # DB에 유저 등록
        user = get_user_model().objects.create_user(
            username = username,
            password = password,
            email = email
        )
        
        return Response({
            "message":"회원가입 성공",
            "data":{
                "username":user.username,
                "email":user.email,
            },
        }, status=status.HTTP_201_CREATED)


def login_page(request):
    if request.method == 'POST':
        return redirect('games:game_test_page', 4)
    return render(request, 'accounts/login.html')

def signup_page(request):
    if request.method == 'POST':
        # pass
        return redirect('accounts:login_page')
    return render(request, 'accounts/signup.html')