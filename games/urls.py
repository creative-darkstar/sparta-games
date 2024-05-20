from django.urls import path
from . import views


app_name = "games"

urlpatterns = [
    path("api/list/", views.GameListAPIView.as_view(), name="game_list"),
    path("api/list/<int:game_pk>/", views.GameDetailAPIView.as_view(), name="game_list"),
    path("api/list/<int:game_pk>/like/", views.GameLikeAPIView.as_view(), name="game_like"),
    path("api/list/<int:game_pk>/star/", views.GameStarAPIView.as_view(), name="game_star"),
    path("api/list/<int:game_pk>/comments/", views.CommentAPIView.as_view(), name="comments"),
    path('api/comment/<int:comment_id>', views.CommentDetailAPIView.as_view(), name='comment_detail'),
    # 게임 등록 Api
    path("api/list/<int:game_pk>/register/", views.game_register, name="game_register"),

    # 게임 등록 테스트용 페이지 뷰
    path("list/<int:game_pk>/", views.game_detail_view, name="game_test_page"),
]
