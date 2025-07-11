from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib import messages

from proposals.forms import ProposalCommentForm, ProposalReplyForm
from proposals.models import ProposalPost, ProposalComment, ProposalReply, ProposalReplyEvidence

from articles.models import Article

from community.apis import get_gemini_response
from django.urls import reverse

# @login_required(login_url='accounts:login')
def home(request):
    """
    정책 제안 게시글 리스트 출력
    """
    proposals = ProposalPost.objects.all()

    # 정렬 추가
    sort = request.GET.get('sort', 'popular')

    if sort == 'popular':
        # 인기 점수: (좋아요 수 * 5) + (댓글 수 * 2)
        proposals = sorted(
            proposals,
            key=lambda post: (post.liked.count() * 5 + post.proposal_comments.filter(created_at__isnull=False).count() * 2),
            reverse=True
        )
    else:  # 최신순
        proposals = proposals.filter(created_at__isnull=False).order_by('-created_at')

    return render(request, 'proposals_home.html', {'proposals': proposals})

# @login_required(login_url='accounts:login')
def detail(request, post_id):
    """
    게시글 상세 페이지 출력
    """
    post = get_object_or_404(ProposalPost, id=post_id)

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
            reply = ProposalReply.objects.get(pk=editing_reply_id)
            opened_reply_comment_id = reply.comment.id
        except ProposalReply.DoesNotExist:
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
        comment_form = ProposalCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('proposals:detail', post_id=post_id)
        else:
            messages.error(request, "댓글 내용을 확인해 주세요. ")
    else:
        comment_form = ProposalCommentForm()

    reply_form = None
    if editing_reply_id:
        try:
            reply_obj = ProposalReply.objects.get(id=editing_reply_id)
            reply_form = ProposalReplyForm(instance=reply_obj)
        except ProposalReply.DoesNotExist:
            editing_reply_id = None

    # 정렬/필터 파라미터 받기
    sort = request.GET.get('sort', 'popular')  # 기본값: 인기순
    petition_filter = request.GET.get('filter', '')  # 기본값: 필터링 안 함

    # 기본 쿼리셋
    comments = post.proposal_comments.all().prefetch_related('proposal_replies', 'user')

    # 필터 적용
    if petition_filter == 'petition':
        comments = comments.exclude(link_url__isnull=True).exclude(link_url__exact='')

    # 정렬 적용
    if sort == 'popular':
        comments = sorted(comments, key=lambda c: c.liked.count(), reverse=True)
    else:  # 최신순
        comments = comments.order_by('-created_at')

    # Bets 기준(좋아요*5 + 답댓*2 >= 100)
    for comment in comments:
        likes = comment.liked.count()
        replies = comment.proposal_replies.count()
        comment.is_best = (likes * 5 + replies * 2) >= 20

    # 익명 이름 부여(정책 제안의 경우 답글만)
    all_reply_entries = []
    for comment in comments:
        for reply in comment.proposal_replies.all():
            if reply.created_at:  # created_at이 있는 답글만
                all_reply_entries.append((reply.user.id, reply.created_at))

    all_reply_entries.sort(key=lambda x: x[1])

    # 익명 번호 매핑 (댓글 작성자는 제외해도 상관 없음)
    anon_map = {}
    counter = 1
    for user_id, _ in all_reply_entries:
        if user_id not in anon_map:
            anon_map[user_id] = f"익명{counter}"
            counter += 1

    # reply 객체에 익명 이름 부여
    for comment in comments:
        for reply in comment.proposal_replies.all():
            reply.anonymous_name = anon_map.get(reply.user.id, None)

    # 추천 아티클은 최신순 5개
    recommended_articles = Article.objects.order_by('-created_at')[:5]

    context = {
        'post': post,
        # 정렬/필터링된 댓글 목록 comments 추가
        'comments' : comments,
        # 추천 아티클 추가
        'recommended_articles': recommended_articles,
        'comment_form': comment_form,
        'reply_form': reply_form,
        'editing_comment_id': editing_comment_id,
        'editing_reply_id': editing_reply_id,
        'opened_reply_comment_id': opened_reply_comment_id,
    }

    return render(request, 'proposals_detail.html', context)

#정책 제안 게시판의 경우 post도 좋아요 가능
@login_required(login_url='accounts:login')
def detail_post_like(request, post_id):
    post = get_object_or_404(ProposalPost, id=post_id)
    if request.user in post.liked.all():
        post.liked.remove(request.user)
    else:
        post.liked.add(request.user)
    return redirect('proposals:detail', post_id)

#스크랩 기능 추가
@login_required(login_url='accounts:login')
def detail_post_scrap(request, post_id):
    post = get_object_or_404(ProposalPost, id=post_id)
    if request.user in post.scrapped.all():
        post.scrapped.remove(request.user)
    else:
        post.scrapped.add(request.user)
    return redirect('proposals:detail', post_id)

@login_required(login_url='accounts:login')
def detail_comment_create(request, post_id):
    """
    댓글 등록
    """
    if(request.method == 'POST'):
        form = ProposalCommentForm(request.POST)
        if(form.is_valid()):
            comment = form.save(commit=False)
            comment.user = request.user
            
            comment.proposal = get_object_or_404(ProposalPost, id=post_id)

            comment.save()
            return redirect('proposals:detail', comment.proposal.pk)
    else:
        form = ProposalCommentForm()
    context = {
        'form': form,
    }
    return render(request,'proposals_detail.html', context)

@login_required(login_url='accounts:login')
def detail_comment_update(request, post_id, comment_id):
    """
    댓글 수정
    """
    post = get_object_or_404(ProposalPost, id=post_id)
    comment = get_object_or_404(ProposalComment, id=comment_id)

    if request.user != comment.user:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('proposals:detail', post.pk)

    if request.method == 'POST':
        form = ProposalCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('proposals:detail', post.pk)

    else:
        form = ProposalCommentForm(instance=comment)
        
    context = {
        'post': post,
        'comment_form': form,
        'editing_comment_id': comment.id,
    }
    return render(request, 'proposals_detail.html', context)


@login_required(login_url='accounts:login')
def detail_comment_delete(request, post_id, comment_id):
    """
    댓글 삭제
    """
    post = get_object_or_404(ProposalPost, id=post_id)
    comment = get_object_or_404(ProposalComment, id=comment_id)

    if request.user != comment.user:
        messages.error(request, "삭제 권한이 없습니다.")

    if request.method == 'POST':
        comment.delete()

    return redirect('proposals:detail', post.pk)

@login_required(login_url='accounts:login')
def detail_comment_like(request, post_id, comment_id):
    """
    좋아요 기능
    """
    post = get_object_or_404(ProposalPost, id=post_id)
    comment = get_object_or_404(ProposalComment, id=comment_id)

    if request.user == comment.user:
        messages.error(request, "본인이 작성한 댓글은 추천할 수 없습니다.")
        return redirect('proposals:detail', post.pk)
    else:
        #좋아요 토글 추가
        if request.user in comment.liked.all():
            comment.liked.remove(request.user)
        else:
            comment.liked.add(request.user)
    return redirect('{}#comment_{}'.format(
        resolve_url('proposals:detail', post_id=post_id), comment_id
    ))

@login_required(login_url='accounts:login')
def detail_comment_link(request, post_id, comment_id):
    """
    제안 댓글에 링크 추가/수정
    """
    comment = get_object_or_404(ProposalComment, pk=comment_id, proposal__id=post_id)
    
    if request.method == "POST":
        link_url = request.POST.get("link_url")
        comment.link_url = link_url
        comment.save()
        return redirect('{}?open_reply={}#comment_{}'.format(
            resolve_url('proposals:detail', post_id=post_id), comment.id, comment.id
        ))

    return redirect('proposals:detail', post_id=post_id)

@login_required(login_url='accounts:login')
def detail_reply_create(request, post_id, comment_id):
    """
    답글 생성
    """
    if request.method == 'POST':
        form = ProposalReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.comment = get_object_or_404(ProposalComment, id=comment_id)
            reply.save()
            return redirect('proposals:detail', post_id=post_id)
    else:
        form = ProposalReplyForm()

    context = {
        'form': form,
    }
    return render(request, 'proposals_detail.html', context)

@login_required(login_url='accounts:login')
def detail_reply_update(request, post_id, comment_id, reply_id):
    """
    답글 수정
    """
    post = get_object_or_404(ProposalPost, id=post_id)
    #comment = get_object_or_404(ProposalComment, id=comment_id)
    reply = get_object_or_404(ProposalReply, id=reply_id)

    if request.user != reply.user:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('proposals:detail', post.pk)

    if request.method == 'POST':
        if request.POST.get("form_type") == "reply_update":
            form = ProposalReplyForm(request.POST, instance=reply)
            if form.is_valid():
                form.save()
                # 수정 완료 후 리다이렉트 시
                return redirect(f"/proposals/{post.pk}/?open_reply={comment_id}#reply_{reply.id}")


    else:
        return redirect(f'/proposals/{post.pk}/?edit_reply={reply.id}#reply_{reply.id}')

    form = ProposalReplyForm(instance=reply)
    context = {
        'post': post,
        'editing_reply_id': reply.id,
        'reply_form': form,
    }
    return render(request, 'proposals_detail.html', context)

@login_required(login_url='accounts:login')
def detail_reply_delete(request, post_id, comment_id, reply_id):
    """
    답글 삭제
    """
    post = get_object_or_404(ProposalPost, id=post_id)
    #comment = get_object_or_404(ProposalComment, id=comment_id)
    reply = get_object_or_404(ProposalReply, id=reply_id)

    if request.user != reply.user:
        messages.error(request, "삭제 권한이 없습니다.")

    if request.method == 'POST':
        reply.delete()

    return redirect('proposals:detail', post.pk)

@login_required(login_url='accounts:login')
def detail_reply_like(request, post_id, comment_id, reply_id):
    """
    답글 좋아요
    """
    post = get_object_or_404(ProposalPost, id=post_id)
    #comment = get_object_or_404(ProposalComment, id=comment_id)
    reply = get_object_or_404(ProposalReply, id=reply_id)

    if request.user == reply.user:
        messages.error(request, "본인이 작성한 답글은 추천할 수 없습니다.")
        return redirect('proposals:detail', post.pk)
    else:
        #좋아요 토글 추가
        if request.user in reply.liked.all():
            reply.liked.remove(request.user)
        else:
            reply.liked.add(request.user)
    #대댓글 좋아요 시 스크롤 위로 올라가는 문제 수정
    return redirect('{}?open_reply={}#reply_{}'.format(
        resolve_url('proposals:detail', post_id=post_id), comment_id, reply_id
    ))

def detail_reply_ai_response(request, post_id, comment_id):
    """
    답글 AI 근거 자료 생성
    """
    if request.method != 'POST':
        messages.error(request, "잘못된 요청입니다.")
        return redirect ('proposals:detail', post_id=post_id)

    post = get_object_or_404(ProposalPost, id=post_id)
    comment = get_object_or_404(ProposalComment, id=comment_id)
    content = request.POST.get('content')

    if not content:
        commentKeyword = None
        messages.error(request, "답글 내용을 입력하세요.")
        return redirect(f"{reverse('proposals:detail', args=[post_id])}#reply-form")
    else:
        reply = ProposalReply(user=request.user, content=content, comment=comment)
        extra_text = ' 이 글을 분석하여 중심이 되는 핵심 키워드 1~3개를 추출해 주세요. 각 키워드는 댓글의 핵심 주제를 대표해야 합니다. 출력은 오직 쉼표로 구분된 키워드 목록 형태로 작성해 주세요. 단어 수준이 아닌, 사회적 이슈나 제도 등을 나타내는 의미 단위(논리적 단위)의 주제어로 판단해 주세요. 출력 형식 예시: 군 가산점 제도, 여성 역차별, 남성 의무복무'
        full_prompt = content + extra_text
        evidence, link1, link2, link3, link4 = get_gemini_response(content, full_prompt)
        replyEvidence = ProposalReplyEvidence(reply=reply, keyword=evidence, link1=link1, link2=link2, link3=link3, link4=link4)

        reply_form = ProposalReplyForm(initial={'content': content})

        # 댓글 목록 가져오기
        comments = post.proposal_comments.all().prefetch_related('proposal_replies', 'user')
        replyEvidenceMap = {comment.id: [replyEvidence]}

        # 익명 이름 부여
        all_entries = []
        for c in comments:
            all_entries.append((c.user.id, c.created_at))
            for r in c.proposal_replies.all():
                all_entries.append((r.user.id, r.created_at))

        all_entries.sort(key=lambda x: x[1])
        anon_map = {}
        counter = 1
        for user_id, _ in all_entries:
            if user_id not in anon_map:
                anon_map[user_id] = f"익명{counter}"
                counter += 1

        for c in comments:
            c.anonymous_name = anon_map.get(c.user.id, "익명?")
            for r in c.proposal_replies.all():
                r.anonymous_name = anon_map.get(r.user.id, "익명?")
    
        for c in comments:
            c.is_best = (c.liked.count() * 5 + c.proposal_replies.count() * 2) >= 20

    recommended_articles = Article.objects.order_by('-created_at')[:5]

    comment_form = ProposalCommentForm()
    
    context = {
        'post': post,
        'community_post': post.community_post,
        'comment' : reply.comment,
        'comments': comments,
        'comment_form': comment_form,
        'reply_form': reply_form,
        'replyEvidenceMap': replyEvidenceMap,
        'recommended_articles': recommended_articles,
        'opened_reply_comment_id': comment.id,
    }
        
    return render(request, 'proposals_detail.html', context)