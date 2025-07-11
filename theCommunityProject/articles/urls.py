from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # 아티클 홈/정렬
    path('', views.home, name='home'),

    # 상세 보기
    path('<int:article_id>/', views.detail, name='detail'),

    # 좋아요, 스크랩
    path('<int:article_id>/like/', views.article_like, name='article_like'),
    path('<int:article_id>/scrap/', views.article_scrap, name='article_scrap'),

    # 댓글 CRUD + 좋아요
    path('<int:article_id>/comment/create/', views.comment_create, name='comment_create'),
    path('<int:article_id>/comment/<int:comment_id>/update/', views.comment_update, name='comment_update'),
    path('<int:article_id>/comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('<int:article_id>/comment/<int:comment_id>/like/', views.comment_like, name='comment_like'),

    # 답글 CRUD + 좋아요
    path('<int:article_id>/comment/<int:comment_id>/reply/create/', views.reply_create, name='reply_create'),
    path('<int:article_id>/comment/<int:comment_id>/reply/<int:reply_id>/update/', views.reply_update, name='reply_update'),
    path('<int:article_id>/comment/<int:comment_id>/reply/<int:reply_id>/delete/', views.reply_delete, name='reply_delete'),
    path('<int:article_id>/comment/<int:comment_id>/reply/<int:reply_id>/like/', views.reply_like, name='reply_like'),

    # ai 추가
    path('<int:post_id>/comment/evidence/', views.detail_comment_ai_response, name='detail_comment_ai_response'),
    path('<int:post_id>/detail/comment/<int:comment_id>/reply/evidence/', views.detail_reply_ai_response, name='detail_reply_ai_response'),
]
