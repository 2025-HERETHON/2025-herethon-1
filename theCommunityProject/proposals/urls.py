from django.urls import path
from . import views

app_name = 'proposals'

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:post_id>/', views.detail, name='detail'),
    path('<int:post_id>/like/', views.detail_post_like, name='detail_post_like'),
    path('<int:post_id>/scrap/', views.detail_post_scrap, name='detail_post_scrap'),
    path('<int:post_id>/comment/create/', views.detail_comment_create, name='detail_comment_create'),
    path('<int:post_id>/comment/<int:comment_id>/update/', views.detail_comment_update, name='detail_comment_update'),
    path('<int:post_id>/comment/<int:comment_id>/delete/', views.detail_comment_delete, name='detail_comment_delete'),
    path('<int:post_id>/comment/<int:comment_id>/like/', views.detail_comment_like, name='detail_comment_like'),
    path('<int:post_id>/comment/<int:comment_id>/reply/create/', views.detail_reply_create, name='detail_reply_create'),
    path('<int:post_id>/comment/<int:comment_id>/reply/<int:reply_id>/update/', views.detail_reply_update, name='detail_reply_update'),
    path('<int:post_id>/comment/<int:comment_id>/reply/<int:reply_id>/delete/', views.detail_reply_delete, name='detail_reply_delete'),
    path('<int:post_id>/comment/<int:comment_id>/reply/<int:reply_id>/like', views.detail_reply_like, name='detail_reply_like'),
]