# category/urls.py
from django.urls import path
from . import views

app_name = "category"

urlpatterns = [
    path("", views.category_list, name="list"),
    path("new/", views.category_create, name="create"),
    path("<int:pk>/edit/", views.category_update, name="edit"),
    path("<int:pk>/delete/", views.category_delete, name="delete"),
]
