from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'community'

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:post_id>/', views.detail, name='detail'),
    path('<int:post_id>/comment/create/', views.detail_comment_create, name='detail_comment_create'),
    path('<int:post_id>/comment/<int:comment_id>/update/', views.detail_comment_update, name='detail_comment_update'),
    path('<int:post_id>/comment/<int:comment_id>/delete/', views.detail_comment_delete, name='detail_comment_delete'),
    path('<int:post_id>/comment/<int:comment_id>/like/', views.detail_comment_like, name='detail_comment_like'),
    path('<int:post_id>/comment/<int:comment_id>/reply/create/', views.detail_reply_create, name='detail_reply_create'),
    path('<int:post_id>/comment/<int:comment_id>/reply/<int:reply_id>/update/', views.detail_reply_update, name='detail_reply_update'),
    path('<int:post_id>/comment/<int:comment_id>/reply/<int:reply_id>/delete/', views.detail_reply_delete, name='detail_reply_delete'),
    path('<int:post_id>/comment/<int:comment_id>/reply/<int:reply_id>/like', views.detail_reply_like, name='detail_reply_like'),
    path('<int:post_id>/vote/', views.detail_vote, name='detail_vote'),
    path('<int:post_id>/comment/evidence/', views.detail_comment_ai_response, name='detail_comment_ai_response'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)