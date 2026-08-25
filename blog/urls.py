from django.urls import path
from . import views

urlpatterns = [
    path('blogs/', views.PostList.as_view(), name='post-list'),
    path('blogs/categories/', views.CategoryList.as_view(), name='category-list'),
    path('blogs/tags/', views.TagList.as_view(), name='tag-list'),
    path('blogs/<slug:slug>/', views.PostDetail.as_view(), name='post-detail'),
]
