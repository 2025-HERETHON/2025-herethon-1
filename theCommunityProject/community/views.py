from urllib import request

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib import messages
from django.views.decorators.http import require_POST

from community.forms import CommentForm, ReplyForm
from community.models import Post, Comment, Reply, Vote


# Create your views here.

@login_required(login_url='accounts:login')
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

@login_required(login_url='accounts:login')
def detail(request, post_id):
    """
    게시글 상세 페이지 출력
    """
    post = get_object_or_404(Post, id=post_id)

    #유저가 투표했는지 검사
    voted_choice = None
    if request.user.is_authenticated:
        vote = Vote.objects.filter(post=post, user=request.user).first()
        if vote:
            voted_choice = vote.choice

    profile_images = {
        1 : '/media/profile_image/A.jpg',
        2 : '/media/profile_image/B.jpg',
        3 : '/media/profile_image/C.jpg',
    }

    user_profile_image = profile_images.get(voted_choice, '/media/profile_image/D.jpg')

    #댓글 수정 시, 수정할 댓글 id를 받아옴
    editing_comment_id = request.GET.get('edit_comment')
    #답글 수정 시, 수정할 답글 id를 받아옴
    editing_reply_id = request.GET.get('edit_reply')
    #답글 수정 완료 시, 답글 창 열린 상태 유지하기 위해서 답글이 달린 댓글의 id를 받아옴
    open_reply_comment_id = request.GET.get('open_reply')

    #답글 수정 완료 시 수정 완료한 답글 위치로 스크롤 하기 위해 검사
    opened_reply_comment_id = None
    if editing_reply_id:                                 #수정했거나 수정 예정인 답글이 있는 경우
        editing_reply_id = int(editing_reply_id)
        try:                                             #답글 토글 열림 상태
            reply = Reply.objects.get(pk=editing_reply_id)
            opened_reply_comment_id = reply.comment.id
        except Reply.DoesNotExist:
            editing_reply_id = None
            pass
    elif open_reply_comment_id:                          #답글 창이 열려 있었던 경우
        try:
            opened_reply_comment_id = int(open_reply_comment_id)  #답글 토글이 열려있던 댓글 id 정보 저장
        except ValueError:
            opened_reply_comment_id = None

    #답글 수정 관련 시도 없음, 답글 토글 닫혀있던 경우
    else:
        opened_reply_comment_id = None
        open_reply_comment_id = None

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

    #투표 수(전달 형태: {1: 0, 2: 0, 3: 2})
    print(post.count_votes())

    context = {
        'post': post,
        'comment_form': comment_form,
        'editing_comment_id': int(editing_comment_id) if editing_comment_id else None,
        'editing_reply_id': int(editing_reply_id) if editing_reply_id else None,
        'opened_reply_comment_id': opened_reply_comment_id,
        'reply_form': reply_form,
        'voted_choice': voted_choice,
        'user_profile_image': user_profile_image,
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
def detail_comment_delete(request, post_id, comment_id):
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
        if request.POST.get("form_type") == "reply_update":
            form = ReplyForm(request.POST, instance=reply)
            if form.is_valid():
                form.save()
                # 수정 완료 후 리다이렉트 시
                return redirect(f"/community/{post.pk}/?open_reply={comment_id}#reply_{reply.id}")


    else:
        return redirect(f'/community/{post.pk}/?edit_reply={reply.id}#reply_{reply.id}')

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
    """
    답글 좋아요
    """
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

@login_required(login_url='accounts:login')
def detail_vote(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if Vote.objects.filter(post=post, user=request.user).exists():
        messages.error(request, "이미 투표하셨습니다.")
        return redirect('community:detail', post_id=post.pk)

    selected = int(request.POST.get('selected'))
    if selected not in dict(Vote.choices):
        messages.error(request, "잘못된 선택입니다.")
        return redirect('community:detail', post_id=post.pk)

    Vote.objects.create(post=post, user=request.user, choice=selected)
    return redirect('community:detail', post_id=post.pk)