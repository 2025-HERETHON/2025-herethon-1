from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib import messages
from django.views.decorators.http import require_POST

from community.forms import CommentForm, ReplyForm
from community.models import Post, Comment, Reply


# Create your views here.

def home(request):
    """
    커뮤니티 게시글 리스트 출력
    """
    #kw = 검색어 받아서 게시글 필터링
    kw = request.GET.get('kw', '')
    post_list = Post.objects.order_by('-created_at')
    if kw:
        post_list = post_list.filter(
            Q(title__icontains=kw) |
            Q(option1__icontains=kw) |
            Q(option2__icontains=kw) |
            Q(option3__icontains=kw)).distinct()

    context = {
        'post_list': post_list,
    }
    return render(request, 'community_home.html', context)

#post 정보 넘김
def detail(request, post_id):
    """
    게시글 상세 페이지 출력
    """
    post = get_object_or_404(Post, id=post_id)
    editing_comment_id = request.GET.get('edit')
    editing_reply_id = request.GET.get('edit_reply')


    context = {
        'post': post,
    }
    if(request.method == 'POST'):
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('community:detail', post_id=post_id)
        else:
            messages.error(request, "댓글 내용을 확인해 주세요. ")
    else:
        comment_form = CommentForm()

    reply_form = None
    if editing_reply_id:
        try:
            reply_obj = Reply.objects.get(id=editing_reply_id)
            reply_form = ReplyForm(instance=reply_obj)
        except Reply.DoesNotExist:
            editing_reply_id = None


    context = {
        'post': post,
        'comment_form': comment_form,
        'editing_comment_id': int(editing_comment_id) if editing_comment_id else None,
        'editing_reply_id': int(editing_reply_id) if editing_reply_id else None,
        'reply_form': reply_form,
    }

    return render(request, 'community_detail.html', context)

@login_required(login_url='accounts:login')
def detail_comment_create(request, post_id):
    """
    댓글 등록
    """
    if(request.method == 'POST'):
        form = CommentForm(request.POST)
        if(form.is_valid()):
            comment = form.save(commit=False)
            comment.user = request.user

            comment.post = get_object_or_404(Post, id=post_id)

            comment.save()
            return redirect('community:detail', comment.post.pk)
    else:
        form = CommentForm()
    context = {
        'form': form,
    }
    return render(request,'community_detail.html', context)

@login_required(login_url='accounts:login')
def detail_comment_update(request, post_id, comment_id):
    """
    댓글 수정
    """
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('community:detail', post.pk)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('community:detail', post.pk)

    else:
        form = CommentForm(instance=comment)
    context = {
        'post': post,
        'comment_form': form,
        'editing_comment_id': comment.id,
    }
    return render(request, 'community_detail.html', context)


@login_required(login_url='accounts:login')
def detail_comment_delate(request, post_id, comment_id):
    """
    댓글 삭제
    """
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        messages.error(request, "삭제 권한이 없습니다.")

    if request.method == 'POST':
        comment.delete()

    return redirect('community:detail', post.pk)

@login_required(login_url='accounts:login')
def detail_comment_like(request, post_id, comment_id):
    """
    좋아요 기능
    """
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user:
        messages.error(request, "본인이 작성한 댓글은 추천할 수 없습니다.")
        return redirect('community:detail', post.pk)
    else:
        comment.liked.add(request.user)
    return redirect('{}#comment_{}'.format(
        resolve_url('community:detail', post_id=post_id), comment_id
    ))

@login_required(login_url='accounts:login')
def detail_reply_create(request, post_id, comment_id):
    """
    답글 생성
    """
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.comment = get_object_or_404(Comment, id=comment_id)
            reply.save()
            return redirect('community:detail', post_id=post_id)
    else:
        form = ReplyForm()

    context = {
        'form': form,
    }
    return render(request, 'community_detail.html', context)

@login_required(login_url='accounts:login')
def detail_reply_update(request, post_id, comment_id, reply_id):
    """
    답글 수정
    """
    post = get_object_or_404(Post, id=post_id)
    #comment = get_object_or_404(Comment, id=comment_id)
    reply = get_object_or_404(Reply, id=reply_id)

    if request.user != reply.user:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('community:detail', post.pk)

    if request.method == 'POST':
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            return redirect(f'/community/{post.pk}/?edit_reply={reply.id}')


    else:
        form = ReplyForm(instance=reply)
    context = {
        'post': post,
        'editing_reply_id': reply.id,
        'reply_form': form,
    }
    return render(request, 'community_detail.html', context)

@login_required(login_url='accounts:login')
def detail_reply_delete(request, post_id, comment_id, reply_id):
    """
    답글 삭제
    """
    post = get_object_or_404(Post, id=post_id)
    #comment = get_object_or_404(Comment, id=comment_id)
    reply = get_object_or_404(Reply, id=reply_id)

    if request.user != reply.user:
        messages.error(request, "삭제 권한이 없습니다.")

    if request.method == 'POST':
        reply.delete()

    return redirect('community:detail', post.pk)

@login_required(login_url='accounts:login')
def detail_reply_like(request, post_id, comment_id, reply_id):
    post = get_object_or_404(Post, id=post_id)
    #comment = get_object_or_404(Comment, id=comment_id)
    reply = get_object_or_404(Reply, id=reply_id)

    if request.user == reply.user:
        messages.error(request, "본인이 작성한 답글은 추천할 수 없습니다.")
        return redirect('community:detail', post.pk)
    else:
        reply.liked.add(request.user)
    return redirect('{}#reply_{}'.format(
        resolve_url('community:detail', post_id=post_id), comment_id, reply_id
    ))