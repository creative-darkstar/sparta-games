from django.urls import path
from . import views


app_name = "games"

urlpatterns = [
    path("", views.GameListAPIView.as_view(), name="game_list"),
]
