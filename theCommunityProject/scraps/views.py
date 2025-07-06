from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from community.models import Post

# Create your views here.
def scraps_article(request):
    """
    아티클 스크랩
    """

@login_required(login_url='accounts/login')
def scraps_community(request):
    """
    커뮤니티 스크랩
    """
    community_posts = request.user.scrapped_community_posts.all()
    context = {
        'community_posts': community_posts,
    }
    return render(request, 'scrapped_community.html', context)
