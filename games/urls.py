from django.urls import path
from . import views


app_name = "games"

urlpatterns = [
    path("api/list/", views.GameListAPIView.as_view(), name="game_list"),
    path("api/list/<int:game_pk>/", views.GameDetailView.as_view(), name="game_list"),
]
