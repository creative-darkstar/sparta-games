from django.urls import path
from . import views


app_name = "qnas"

urlpatterns = [
    path("api/post/", views.QnAPostListAPIView.as_view(), name="qna_list"),
    path("api/post/<int:qna_pk>/", views.QnADetailAPIView.as_view(), name="qna_detail"),

    #Templates
    path("", views.qna_main_view, name="qna_main"),
    path("<int:qna_pk>/", views.qna_detail_view, name="qna_detail_page"),
    path("create/", views.qna_create_view, name="qna_create"),
]
