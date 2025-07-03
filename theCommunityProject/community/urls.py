from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:post_id>/', views.detail, name='detail'),
    path('<int:post_id>/comment/create/', views.detail_comment_create, name='detail_comment_create'),
    path('<int:post_id>/comment/<int:comment_id>/update/', views.detail_comment_update, name='detail_comment_update'),
]