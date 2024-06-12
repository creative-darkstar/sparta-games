from django.urls import path
from . import views


app_name = "qnas"

urlpatterns = [
    # ---------- API---------- #
    path("api/post/", views.QnAPostListAPIView.as_view(), name="qna_list"),
    path("api/post/<int:qna_pk>/", views.QnADetailAPIView.as_view(), name="qna_detail"),
    path('api/categories/', views.CategoryListView.as_view(), name='category_list'),

    # ---------- Web---------- #
    path("", views.qna_main_view, name="qna_main"),
    path("<int:qna_pk>/", views.qna_detail_view, name="qna_detail_page"),
    path("create/", views.qna_create_view, name="qna_create"),
    path("<int:qna_pk>/update/", views.qna_update_view, name="qna_update"),
]
