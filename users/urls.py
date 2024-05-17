from django.urls import path
from . import views


app_name = "users"

urlpatterns = [
    path("api/<int:user_pk>/", views.ProfileAPIView.as_view(), name="profile"),
    path("api/<int:user_pk>/password/", views.change_password, name="change_password"),
]
