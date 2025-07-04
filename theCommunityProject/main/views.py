from django.shortcuts import render
from proposals.models import ProposalPost

def home(request):
    return render(request, 'index.html')

def scrapped_proposal_posts(request):
    posts = request.user.scrapped_proposal_posts.all()
    return render(request, 'scrapped_proposal_posts.html', {'posts': posts})