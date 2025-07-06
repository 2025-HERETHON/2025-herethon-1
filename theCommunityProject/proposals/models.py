from django.db import models
from accounts.models import User
from community.models import Post as CommunityPost

class ProposalPost(models.Model):
    #투표 마감된 커뮤니티 Post에서 생성됨
    community_post = models.OneToOneField(CommunityPost, on_delete=models.CASCADE, related_name='proposal_post')
    title = models.CharField(max_length=100)
    question = models.TextField()  # 투표 질문
    result_choice = models.CharField(max_length=100)  # 가장 많이 선택된 항목
    result_percent = models.IntegerField()  # 해당 항목 퍼센트
    created_at = models.DateTimeField(auto_now_add=True)
    liked = models.ManyToManyField(User, related_name='liked_proposal_posts', blank=True)
    # article = models.ForeignKey(Article, on_delete = models.CASCADE)
    scrapped = models.ManyToManyField(User, related_name='scrapped_proposal_posts', blank=True)

    # 가장 많은 투표를 받은 항목의 텍스트 반환
    # 관리자 작성으로 바뀜
    # def get_top_choice(self):
    #     count_votes = self.community_post.count_votes()
    #     top_choice_num = max(count_votes, key=count_votes.get)
    #     return self.community_post.get_option_text(top_choice_num)

#정책 제안(댓글 형식)
class ProposalComment(models.Model):
    proposal = models.ForeignKey(ProposalPost, on_delete=models.CASCADE, related_name='proposal_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    problem = models.TextField()
    solution = models.TextField()
    effect = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    liked = models.ManyToManyField(User, related_name='liked_proposal_comments')
    link_url = models.URLField(null=True, blank=True)

#정책 제안(댓글)에 달린 답글
class ProposalReply(models.Model):
    comment = models.ForeignKey(ProposalComment, on_delete=models.CASCADE, related_name='proposal_replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    liked = models.ManyToManyField(User, related_name='liked_proposal_reply')