from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
@login_required(login_url='accounts/login')
def scraps_article(request):
    """
    아티클 스크랩
    """
    article_posts = request.user.scrapped_article_posts.all()
    context = {
        'article_posts': article_posts,
    }

    return render(request, 'scrapped_article.html', context)

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

@login_required(login_url='accounts/login')
def scraps_proposal(request):
    """
    정책 제안 스크랩
    """
    proposal_posts = request.user.scrapped_proposal_posts.all()
    context = {
        'proposal_posts': proposal_posts,
    }

    return  render(request, 'scrapped_proposal.html', context)