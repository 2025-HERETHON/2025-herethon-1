from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scrap/articles/', views.scrapped_article_posts, name='scrapped_article_posts'),
    path('scrap/community/', views.scrapped_community_posts, name='scrapped_community_posts'),
    path('scrap/proposals/', views.scrapped_proposal_posts, name='scrapped_proposal_posts'),
]