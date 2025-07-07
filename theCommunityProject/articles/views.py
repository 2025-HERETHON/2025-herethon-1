from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib import messages

from .models import Article, ArticleComment, ArticleReply
from .forms import ArticleCommentForm, ArticleReplyForm

from community.models import Post

# 홈: 아티클 목록
@login_required(login_url='accounts:login')
def home(request):
    sort = request.GET.get('sort', 'popular')
    articles = Article.objects.all()

    if sort == 'popular':
        articles = sorted(articles, key=lambda a: (a.liked.count() * 5 + a.article_comments.filter(created_at__isnull=False).count() * 2), reverse=True)
    else:
        articles = articles.filter(created_at__isnull=False).order_by('-created_at')

    return render(request, 'article_home.html', {'articles': articles})

# 상세 보기
@login_required(login_url='accounts:login')
def detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    editing_comment_id = request.GET.get('edit_comment')
    editing_reply_id = request.GET.get('edit_reply')
    open_reply_comment_id = request.GET.get('open_reply')

    opened_reply_comment_id = None
    if editing_reply_id:
        try:
            reply = ArticleReply.objects.get(pk=editing_reply_id)
            opened_reply_comment_id = reply.comment.id
        except ArticleReply.DoesNotExist:
            editing_reply_id = None
    elif open_reply_comment_id:
        try:
            opened_reply_comment_id = int(open_reply_comment_id)
        except ValueError:
            opened_reply_comment_id = None

    if request.method == 'POST':
        comment_form = ArticleCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()
            return redirect('articles:detail', article_id=article_id)
        else:
            messages.error(request, "댓글 내용을 확인해 주세요.")
    else:
        comment_form = ArticleCommentForm()

    reply_form = None
    if editing_reply_id:
        try:
            reply_obj = ArticleReply.objects.get(id=editing_reply_id)
            reply_form = ArticleReplyForm(instance=reply_obj)
        except ArticleReply.DoesNotExist:
            editing_reply_id = None

    # 댓글 목록 가져오기(답글까지 같이 가져옴)        
    comments = article.article_comments.all().prefetch_related('article_replies', 'user')
    
    sort = request.GET.get('sort', 'popular')
    
    if sort == 'popular':
        comments = sorted(comments, key=lambda c: c.liked.count(), reverse=True)
    else:
        comments = comments.order_by('-created_at')

    # 익명 이름 부여
    all_entries = []
    for comment in comments:
        # 더미 코멘트 포함 안 함
        if comment.created_at:
            all_entries.append((comment.user.id, comment.created_at))
        for reply in comment.article_replies.all():
            # 더미 코멘트 포함 안 함
            if reply.created_at:
                all_entries.append((reply.user.id, reply.created_at))
    
    # 작성 시간 순 정렬
    all_entries.sort(key=lambda x: x[1])
    # 익명 번호 매핑
    anon_map = {}
    counter = 1
    for user_id, _ in all_entries:
        if user_id not in anon_map:
            anon_map[user_id] = f"익명{counter}"
            counter += 1
    # 객체에 익명 번호 부여
    for comment in comments:
        comment.anonymous_name = anon_map.get(comment.user.id, "익명?")
        for reply in comment.article_replies.all():
            reply.anonymous_name = anon_map.get(reply.user.id, "익명?")

    #관련된 커뮤니티 게시글(3개까지만 출력)
    related_posts = Post.objects.filter(related_article=article).order_by('-created_at')[:3]

    for post in related_posts:
        post.filtered_comments = post.comments.filter(created_at__isnull=False)

    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
        'related_posts': related_posts,
        'reply_form': reply_form,
        'editing_comment_id': int(editing_comment_id) if editing_comment_id else None,
        'editing_reply_id': int(editing_reply_id) if editing_reply_id else None,
        'opened_reply_comment_id': opened_reply_comment_id,
    }
    return render(request, 'article_detail.html', context)

# 아티클 좋아요
@login_required(login_url='accounts:login')
def article_like(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.user in article.liked.all():
        article.liked.remove(request.user)
    else:
        article.liked.add(request.user)
    return redirect('articles:detail', article_id=article_id)

# 아티클 스크랩
@login_required(login_url='accounts:login')
def article_scrap(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.user in article.scrapped.all():
        article.scrapped.remove(request.user)
    else:
        article.scrapped.add(request.user)
    return redirect('articles:detail', article_id=article_id)

# 댓글 생성
@login_required(login_url='accounts:login')
def comment_create(request, article_id):
    if request.method == 'POST':
        form = ArticleCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.article = get_object_or_404(Article, id=article_id)
            comment.save()
    return redirect('articles:detail', article_id=article_id)

# 댓글 수정
@login_required(login_url='accounts:login')
def comment_update(request, article_id, comment_id):
    comment = get_object_or_404(ArticleComment, id=comment_id)
    if request.user != comment.user:
        messages.error(request, "수정 권한이 없습니다.")
        return redirect('articles:detail', article_id)

    if request.method == 'POST':
        form = ArticleCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('articles:detail', article_id)

    return redirect(f'/articles/{article_id}/?edit_comment={comment_id}#comment_{comment_id}')

# 댓글 삭제
@login_required(login_url='accounts:login')
def comment_delete(request, article_id, comment_id):
    comment = get_object_or_404(ArticleComment, id=comment_id)
    if request.user == comment.user and request.method == 'POST':
        comment.delete()
    return redirect('articles:detail', article_id=article_id)

# 댓글 좋아요
@login_required(login_url='accounts:login')
def comment_like(request, article_id, comment_id):
    comment = get_object_or_404(ArticleComment, id=comment_id)
    if request.user != comment.user:
        if request.user in comment.liked.all():
            comment.liked.remove(request.user)
        else:
            comment.liked.add(request.user)
    else:
        messages.error(request, "본인 댓글은 추천할 수 없습니다.")
    return redirect('{}#comment_{}'.format(resolve_url('articles:detail', article_id=article_id), comment_id))

# 답글 생성
@login_required(login_url='accounts:login')
def reply_create(request, article_id, comment_id):
    if request.method == 'POST':
        form = ArticleReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.comment = get_object_or_404(ArticleComment, id=comment_id)
            reply.save()
    return redirect('articles:detail', article_id=article_id)

# 답글 수정
@login_required(login_url='accounts:login')
def reply_update(request, article_id, comment_id, reply_id):
    reply = get_object_or_404(ArticleReply, id=reply_id)
    if request.user != reply.user:
        messages.error(request, "수정 권한이 없습니다.")
        return redirect('articles:detail', article_id)

    if request.method == 'POST':
        form = ArticleReplyForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            return redirect(f"/articles/{article_id}/?open_reply={comment_id}#reply_{reply.id}")

    return redirect(f'/articles/{article_id}/?edit_reply={reply.id}#reply_{reply.id}')

# 답글 삭제
@login_required(login_url='accounts:login')
def reply_delete(request, article_id, comment_id, reply_id):
    reply = get_object_or_404(ArticleReply, id=reply_id)
    if request.user == reply.user and request.method == 'POST':
        reply.delete()
    return redirect('articles:detail', article_id=article_id)

# 답글 좋아요
@login_required(login_url='accounts:login')
def reply_like(request, article_id, comment_id, reply_id):
    reply = get_object_or_404(ArticleReply, id=reply_id)
    if request.user != reply.user:
        if request.user in reply.liked.all():
            reply.liked.remove(request.user)
        else:
            reply.liked.add(request.user)
    else:
        messages.error(request, "본인 답글은 추천할 수 없습니다.")
    return redirect('{}?open_reply={}#reply_{}'.format(resolve_url('articles:detail', article_id=article_id), comment_id, reply_id))
