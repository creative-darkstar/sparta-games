from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import re
from rest_framework import status


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
            return Response({"error_message":"올바른 username을 입력해주세요."})
        elif get_user_model().objects.filter(username=username).exists():
            return Response({"error_message":"이미 존재하는 username입니다."})
        
        # password 유효성 검사
        if not self.PASSWORD_PATTERN.match(password):
            return Response({"error_message":"올바른 password.password_check를 입력해주세요."})
        elif not password == password_check:
            return Response({"error_message":"암호를 확인해주세요."})

        # email 유효성 검사
        if not self.EMAIL_PATTERN.match(email):
            return Response({"error_message":"올바른 email을 입력해주세요."})
        elif get_user_model().objects.filter(email=email).exists():
            return Response({"error_message":"이미 존재하는 email입니다.."})
        

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