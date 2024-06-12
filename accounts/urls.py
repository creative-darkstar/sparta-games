from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
    TokenVerifyView,
)


app_name = "accounts"

urlpatterns = [
    # ---------- API---------- #
    path("api/login/", TokenObtainPairView.as_view(), name='login'),
    path("api/refresh/", TokenRefreshView.as_view(), name='refresh_token'),
    path("api/logout/", TokenBlacklistView.as_view(), name='logout'),
    path("api/signup/", views.SignUpAPIView.as_view(), name='signup'),
    path("api/verify/", TokenVerifyView.as_view(), name='verify'),

    # ---------- Web---------- #
    path('login/', views.login_page, name='login_page'),
    path('signup/', views.signup_page, name='signup_page'),
]
