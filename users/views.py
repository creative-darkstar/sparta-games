from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def delete(self, request, user_pk):
        check_password = self.request.data.get("password")
        user = get_object_or_404(get_user_model(), pk=user_pk, is_active=True)

        # 탈퇴하려는 유저와 정보가 일치하는지 확인
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
