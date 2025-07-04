from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scrapped/', views.scrapped_proposal_posts, name='scrapped_proposal_posts'),
]