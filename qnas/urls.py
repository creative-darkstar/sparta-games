from django.urls import path
from . import views


app_name = "qnas"

urlpatterns = [
    path("api/post/", views.QnAPostListAPIView.as_view(), name="qna_list"),
]
