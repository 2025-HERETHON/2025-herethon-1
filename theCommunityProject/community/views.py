
from email.quoprimime import unquote
from urllib import request
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST

from community.apis import get_gemini_response
from community.forms import CommentForm, ReplyForm
from community.models import Post, Comment, Reply, Vote, CommentEvidence, ReplyEvidence

from articles.models import Article


# Create your views here.

@login_required(login_url='accounts:login')
def home(request):
    """
    커뮤니티 게시글 리스트 출력
    """
    #kw = 검색어 받아서 게시글 필터링
    kw = request.GET.get('kw', '')
    post_list = Post.objects.order_by('-created_at')

    if post_list:
        for post in post_list:

            post.filtered_comments = post.comments.filter(created_at__isnull=False)
            print(post.title, post.filtered_comments.count())


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

    # 추천 아티클은 일단 임시로 최신순 5개로 정해둠
    recommended_articles = Article.objects.all().order_by('-created_at')[:5]

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

    # 댓글 목록 가져오기(답글까지 같이 가져옴)
    comments = post.comments.all().prefetch_related('replies', 'user').filter(created_at__isnull=False)

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
        for reply in comment.replies.all():
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
        print(f"comment id={comment.id}, anonymous_name={comment.anonymous_name}")
        for reply in comment.replies.all():
            reply.anonymous_name = anon_map.get(reply.user.id, "익명?")
    #투표 수(전달 형태: {1: 0, 2: 0, 3: 2})
    print(post.count_votes())

    #투표 항목에 따른 댓글 필터링(아마 detail에서는 쓸 일 없을 것 같은데 혹시 몰라 남겨둡니다)
    comments_modifing = post.comments.filter(created_at__isnull=False)
    vote_choices = [1, 2, 3]
    comments_by_choice = {}

    for choice in vote_choices:
        comments_modifing = comments_modifing.filter(
            post=post,
            user__vote__post=post,
            user__vote__choice=choice,
        ).distinct()  # 중복 방지 distinct()
        #프론트 전달용 딕셔너리 - comments_by_choice
        comments_by_choice[choice] = comments_modifing

    context = {
        'post': post,
        'comments' : comments,
        'comments_by_choice' : comments_by_choice,
        # 추천 아티클 추가
        'recommended_articles': recommended_articles,
        'comment_form': comment_form,
        'editing_comment_id': int(editing_comment_id) if editing_comment_id else None,
        'editing_reply_id': int(editing_reply_id) if editing_reply_id else None,
        'opened_reply_comment_id': opened_reply_comment_id,
        'reply_form': reply_form,
        'now' : 0,
    }

    return render(request, 'community_detail.html', context)

@login_required(login_url='accounts:login')
def detail_comment_create(request, post_id, now):
    """
    댓글 등록
    """
    if(request.method == 'POST'):
        form = CommentForm(request.POST)
        if(form.is_valid()):
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = get_object_or_404(Post, id=post_id)
            comment.created_at = timezone.now()

            # 투표 항목에 따른 프로필 이미지
            voted_choice = None
            if request.user.is_authenticated:
                vote = Vote.objects.filter(post=comment.post, user=request.user).first()
                if vote:
                    voted_choice = vote.choice

            profile_images = {
                1: '/media/profile_image/A.jpg',
                2: '/media/profile_image/B.jpg',
                3: '/media/profile_image/C.jpg',
            }

            comment.image = profile_images.get(voted_choice, '/media/profile_image/D.jpg')

            comment.save()

            if(now == 1):
                return redirect('community:detail_comment_detail', post_id=post_id)
            else:
                return redirect('community:detail', comment.post.pk)
    else:
        form = CommentForm()
    context = {
        'form': form,
    }
    if(now == 1):
        return render(request, 'community_detail_comment.html', context)
    return render(request,'community_detail.html', context)

@login_required(login_url='accounts:login')
def detail_comment_update(request, post_id, comment_id, now):
    """
    댓글 수정
    """
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        messages.error(request, '수정 권한이 없습니다.')
        if (now == 1):
            return redirect('community:detail_comment_detail', post_id=post_id)
        else:
            return redirect('community:detail', comment.post.pk)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            if (now == 1):
                return redirect('community:detail_comment_detail', post_id=post_id)
            else:
                return redirect('community:detail', comment.post.pk)

    else:
        form = CommentForm(instance=comment)
    context = {
        'post': post,
        'comment_form': form,
        'editing_comment_id': comment.id,
    }
    if (now == 1):
        return render(request, 'community_detail_comment.html', context)
    return render(request, 'community_detail.html', context)


@login_required(login_url='accounts:login')
def detail_comment_delete(request, post_id, comment_id, now):
    """
    댓글 삭제
    """
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        messages.error(request, "삭제 권한이 없습니다.")

    if request.method == 'POST':
        comment.delete()

    if (now == 1):
        return redirect('community:detail_comment_detail', post_id=post_id)
    else:
        return redirect('community:detail', comment.post.pk)

@login_required(login_url='accounts:login')
def detail_comment_like(request, post_id, comment_id, now):
    """
    좋아요 기능
    """
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user:
        messages.error(request, "본인이 작성한 댓글은 추천할 수 없습니다.")
        if (now == 1):
            return redirect('community:detail_comment_detail', post_id=post_id)
        else:
            return redirect('community:detail', comment.post.pk)
    else:
        if request.user in comment.liked.all():
            comment.liked.remove(request.user)
        else:
            comment.liked.add(request.user)
    if (now == 1):
        return redirect('{}#comment_{}'.format(
            resolve_url('community:detail_comment_detail', post_id=post_id), comment_id
        ))
    else:
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

            # 투표 항목에 따른 프로필 이미지
            voted_choice = None
            if request.user.is_authenticated:
                vote = Vote.objects.filter(post=reply.comment.post, user=request.user).first()
                if vote:
                    voted_choice = vote.choice
                # else:
                #     messages.error(request, "투표하지 않은 사용자는 답글을 작성할 수 없습니다. ")
                #     return redirect('community:detail_comment_detail', post_id=post_id)

            profile_images = {
                1: '/media/profile_image/A.jpg',
                2: '/media/profile_image/B.jpg',
                3: '/media/profile_image/C.jpg',
            }

            reply.image = profile_images.get(voted_choice, '/media/profile_image/D.jpg')
            reply.save()
            return redirect('community:detail_comment_detail', post_id=post_id)
    else:
        form = ReplyForm()

    context = {
        'form': form,
    }
    return render(request, 'community_detail_comment.html', context)

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
        return redirect('community:detail_comment_detail', post.pk)

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
    return render(request, 'community_detail_comment.html', context)

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

    return redirect('community:detail_comment_detail', post.pk)

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
        return redirect('community:detail_comment_detail', post.pk)
    else:
        if request.user in reply.liked.all():
            reply.liked.remove(request.user)
        else:
            reply.liked.add(request.user)
    return redirect('{}#reply_{}'.format(
        resolve_url('community:detail_comment_detail', post_id=post_id), comment_id, reply_id
    ))

@login_required(login_url='accounts:login')
def detail_vote(request, post_id, now):
    post = get_object_or_404(Post, id=post_id)

    if Vote.objects.filter(post=post, user=request.user).exists():
        messages.error(request, "이미 투표하셨습니다.")
        return redirect('community:detail', post_id=post.pk)

    selected = int(request.POST.get('selected'))
    if selected not in dict(Vote.choices):
        messages.error(request, "잘못된 선택입니다.")
        if (now == 1):
            return redirect('community:detail_comment_detail', post_id=post_id)
        else:
            return redirect('community:detail', post.pk)

    Vote.objects.create(post=post, user=request.user, choice=selected)
    if (now == 1):
        return redirect('community:detail_comment_detail', post_id=post_id)
    else:
        return redirect('community:detail', post.pk)

def detail_comment_ai_response(request, post_id, now):
    """
    댓글 AI 근거 자료 생성
    """
    if request.method != 'POST':
        messages.error(request, "잘못된 요청입니다.")
        return redirect ('community:detail', post_id=post_id)

    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content')

    if not content:
        commentKeyword = None
        messages.error(request, "댓글 내용을 입력하세요.")
        if (now == 1):
            return redirect(f"{reverse('community:detail_comment_detail', args=[post_id])}#comment-form")
        else:
            return redirect(f"{reverse('community:detail', args=[post_id])}#comment-form")                          #수정해야함
    else:
        comment = Comment(user=request.user, content=content, post=post, created_at=None)
        comment.save()
        extra_text = ' 이 글을 분석하여 중심이 되는 핵심 키워드 1~3개를 추출해 주세요. 각 키워드는 댓글의 핵심 주제를 대표해야 합니다. 출력은 오직 쉼표로 구분된 키워드 목록 형태로 작성해 주세요. 단어 수준이 아닌, 사회적 이슈나 제도 등을 나타내는 의미 단위(논리적 단위)의 주제어로 판단해 주세요. 출력 형식 예시: 군 가산점 제도, 여성 역차별, 남성 의무복무'
        full_prompt = content + extra_text
        evidence, link1, link2, link3, link4 = get_gemini_response(content, full_prompt)
        commentEvidence = CommentEvidence.objects.create(comment=comment, keyword=evidence, link1=link1, link2=link2, link3=link3, link4=link4)

        comment_form = CommentForm(initial={'content': content})

        context = {
            'post': post,
            'comments': post.comments.filter(created_at__isnull=False),
            'comment_form': comment_form,
            'commentEvidence': commentEvidence,
            'now': now,
        }

        if(now == 1):
            return  render(request, 'community_detail_comment.html', context)
        return render(request, 'community_detail.html', context)

# 스크랩 함수 추가
@login_required(login_url='accounts:login')
def detail_post_scrap(request, post_id, now):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.scrapped.all():
        post.scrapped.remove(request.user)
    else:
        post.scrapped.add(request.user)

    if (now == 1):
        return redirect('community:detail_comment_detail', post_id=post_id)
    else:
        return redirect('community:detail', post.pk)

def detail_comment_detail(request, post_id):
    """
    댓글 상세 페이지 출력
    """
    post = get_object_or_404(Post, id=post_id)
    # 댓글 수정 시, 수정할 댓글 id를 받아옴
    editing_comment_id = request.GET.get('edit_comment')
    # 답글 수정 시, 수정할 답글 id를 받아옴
    editing_reply_id = request.GET.get('edit_reply')
    # 답글 수정 완료 시, 답글 창 열린 상태 유지하기 위해서 답글이 달린 댓글의 id를 받아옴
    open_reply_comment_id = request.GET.get('open_reply')

    # 답글 수정 완료 시 수정 완료한 답글 위치로 스크롤 하기 위해 검사
    opened_reply_comment_id = None
    if editing_reply_id:  # 수정했거나 수정 예정인 답글이 있는 경우
        editing_reply_id = int(editing_reply_id)
        try:  # 답글 토글 열림 상태
            reply = Reply.objects.get(pk=editing_reply_id)
            opened_reply_comment_id = reply.comment.id
        except Reply.DoesNotExist:
            editing_reply_id = None
            pass
    elif open_reply_comment_id:  # 답글 창이 열려 있었던 경우
        try:
            opened_reply_comment_id = int(open_reply_comment_id)  # 답글 토글이 열려있던 댓글 id 정보 저장
        except ValueError:
            opened_reply_comment_id = None

    # 답글 수정 관련 시도 없음, 답글 토글 닫혀있던 경우
    else:
        opened_reply_comment_id = None
        open_reply_comment_id = None

    if (request.method == 'POST'):
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('community:detail_comment_detail', post_id=post_id)
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

    recommended_articles = Article.objects.all().order_by('-created_at')[:5]

    # # 댓글 목록 가져오기(답글까지 같이 가져옴)
    comments = post.comments.all().prefetch_related('replies', 'user').filter(created_at__isnull=False)
    #
    # sort = request.GET.get('sort', 'popular')
    #
    # if sort == 'popular':
    #     comments = sorted(comments, key=lambda c: c.liked.count(), reverse=True)
    # else:
    #     comments = comments.order_by('-created_at')

    # 익명 이름 부여
    all_entries = []
    for comment in comments :
        # 더미 코멘트 포함 안 함
        if comment.created_at:
            all_entries.append((comment.user.id, comment.created_at))
        for reply in comment.replies.all():
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
        print(f"comment id={comment.id}, anonymous_name={comment.anonymous_name}")
        for reply in comment.replies.all():
            reply.anonymous_name = anon_map.get(reply.user.id, "익명?")
    # 투표 수(전달 형태: {1: 0, 2: 0, 3: 2})
    print(post.count_votes())

    # 투표 항목에 따른 댓글 필터링
    comments_modifing = post.comments.filter(created_at__isnull=False)
    vote_choices = [1, 2, 3]
    comments_by_choice = {}

    for choice in vote_choices:
        comments_modifing = comments_modifing.filter(
            post=post,
            user__vote__post=post,
            user__vote__choice=choice,
        ).distinct()  # 중복 방지 distinct()
        # 프론트 전달용 딕셔너리 - comments_by_choice
        comments_by_choice[choice] = comments_modifing

    context = {
        'post': post,
        'comments': comments,
        'comments_by_choice' : comments_by_choice,
        'replies' : Reply.objects.filter(created_at__isnull=False),
        'comment_form': comment_form,
        'editing_comment_id': int(editing_comment_id) if editing_comment_id else None,
        'editing_reply_id': int(editing_reply_id) if editing_reply_id else None,
        'opened_reply_comment_id': opened_reply_comment_id,
        'reply_form': reply_form,
        'recommended_articles': recommended_articles,
        'now':1,
    }
    return render(request, 'community_detail_comment.html', context)


def detail_reply_ai_response(request, post_id, comment_id):
    """
    답글 AI 근거 자료 생성
    """
    if request.method != 'POST':
        messages.error(request, "잘못된 요청입니다.")
        return redirect ('community:detail_comment_detail', post_id=post_id)

    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)
    content = request.POST.get('content')

    if not content:
        messages.error(request, "답글 내용을 입력하세요.")
        return redirect(f"{reverse('community:detail_comment_detail', args=[post_id])}#comment-form")
    else:
        reply = Reply(user=request.user, content=content, comment=comment, created_at=None)
        reply.save()
        extra_text = ' 이 글을 분석하여 중심이 되는 핵심 키워드 1~3개를 추출해 주세요. 각 키워드는 댓글의 핵심 주제를 대표해야 합니다. 출력은 오직 쉼표로 구분된 키워드 목록 형태로 작성해 주세요. 단어 수준이 아닌, 사회적 이슈나 제도 등을 나타내는 의미 단위(논리적 단위)의 주제어로 판단해 주세요. 출력 형식 예시: 군 가산점 제도, 여성 역차별, 남성 의무복무'
        full_prompt = content + extra_text
        evidence, link1, link2, link3, link4 = get_gemini_response(content, full_prompt)
        replyEvidence = ReplyEvidence.objects.create(reply=reply, keyword=evidence, link1=link1, link2=link2, link3=link3, link4=link4)
        print('테스트' + replyEvidence.keyword)
        reply_form = ReplyForm(initial={'content': content})
        comment_form = CommentForm()

        context = {
            'post': comment.post,
            'comment': reply.comment,
            'comments': reply.comment.post.comments.filter(created_at__isnull=False),
            'reply_form': reply_form,
            'comment_form':comment_form,
            'replyEvidence': replyEvidence,
            'opened_reply_section': comment.id,
        }

        return render(request, 'community_detail_comment.html', context)
