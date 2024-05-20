import re

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 유효성 검사 정규식 패턴
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

    def get(self, request, user_pk):
        user = get_object_or_404(get_user_model(), pk=user_pk, is_active=True)
        profile_image = user.image.url if user.image else '/image/user.png/'
        return Response({
            "username": user.username,
            "profile_image": profile_image,
            "email": user.email,
        }, status=status.HTTP_200_OK)

    def put(self, request, user_pk):
        check_password = self.request.data.get("password")
        user = get_object_or_404(get_user_model(), pk=user_pk, is_active=True)

        # 현재 로그인한 유저와 수정 대상 회원이 일치하는지 확인
        if request.user.id != user.pk:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # 유저 비밀번호가 일치하지 않으면
        if user.check_password(check_password) is False:
            return Response(
                {"message": "비밀번호가 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 이메일 검증
        email = self.request.data.get('email', user.email)
        if not self.EMAIL_PATTERN.match(email):
            return Response({"error_message": "올바른 email을 입력해주세요."})
        elif get_user_model().objects.filter(email=email).exists():
            return Response({"error_message": "이미 존재하는 email입니다.."})

        user.email = email
        user.image = self.request.data.get('image', user.image)
        user.save()

        return Response(
            {
                "message": "회원 정보 수정 완료",
                "data": {
                    "email": user.email,
                    "image": user.image.url
                }
            },
            status=status.HTTP_202_ACCEPTED
        )

    def delete(self, request, user_pk):
        check_password = self.request.data.get("password")
        user = get_object_or_404(get_user_model(), pk=user_pk, is_active=True)

        # 현재 로그인한 유저와 탈퇴 대상 회원이 일치하는지 확인
        if request.user.id != user.pk:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # 유저 비밀번호가 일치하지 않으면
        if user.check_password(check_password) is False:
            return Response(
                {"message": "비밀번호가 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 유저 비밀번호가 일치한다면
        user.is_active = False
        user.save()
        return Response(
            {
                "message": f"회원 탈퇴 완료 (회원 아이디: {user.username})"
            },
            status=status.HTTP_200_OK
        )


@api_view(["PUT"])
def change_password(request, user_pk):
    # 유효성 검사 정규식 패턴
    PASSWORD_PATTERN = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,32}$')

    user = get_object_or_404(get_user_model(), pk=user_pk, is_active=True)

    check_password = request.data.get("password")
    new_password = request.data.get("new_password")
    new_password_check = request.data.get("new_password_check")

    # 현재 로그인한 유저와 비밀번호 수정 대상 회원이 일치하는지 확인
    if request.user.id != user.pk:
        return Response(status=status.HTTP_403_FORBIDDEN)

    # 유저 비밀번호가 일치하지 않으면
    if user.check_password(check_password) is False:
        return Response(
            {"message": "비밀번호가 일치하지 않습니다."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # new password 유효성 검사
    if not PASSWORD_PATTERN.match(new_password):
        return Response({"error_message": "올바른 password와 password_check를 입력해주세요."})
    elif not new_password == new_password_check:
        return Response({"error_message": "동일한 password와 password_check를 입력해주세요."})

    # 유저 비밀번호가 일치한다면
    user.set_password(new_password)
    user.save()
    return Response(
        {
            "message": f"비밀번호 수정 완료 (회원 아이디: {user.username})"
        },
        status=status.HTTP_200_OK
    )
