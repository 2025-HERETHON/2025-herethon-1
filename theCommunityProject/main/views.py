from django.shortcuts import render
from articles.models import Article
from community.models import Post
from proposals.models import ProposalPost

# def home(request):
#     return render(request, 'index.html')

def scrapped_article_posts(request):
    posts = request.user.scrapped_article_posts.all()
    return render(request, 'scrapped_article_posts.html', {'posts': posts})

def scrapped_community_posts(request):
    posts = request.user.scrapped_community_posts.all()
    return render(request, 'scrapped_community_posts.html', {'posts': posts})

def scrapped_proposal_posts(request):
    posts = request.user.scrapped_proposal_posts.all()
    return render(request, 'scrapped_proposal_posts.html', {'posts': posts})