from django.urls import path
from scraps import views

app_name = "scraps"

urlpatterns = [
    path('article/', views.scraps_article, name='scraps_article'),
    path('community/', views.scraps_community, name='scraps_community'),
    path('proposal/', views.scraps_proposal, name='scraps_proposal'),
]