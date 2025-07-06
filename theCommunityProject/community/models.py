from datetime import timedelta

from django.db import models

from accounts.models import User


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    option1 = models.CharField(max_length=100)
    option2 = models.CharField(max_length=100)
    option3 = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    finish_at = models.DateTimeField(blank=True, null=True)
    #filtered_comments = models.IntegerField(default=0)

    # article = models.ForeignKey(Article, on_delete = models.CASCADE)
    scrapped = models.ManyToManyField(User, related_name='scrapped_community_posts', blank=True)

    def save(self, *args, **kwargs):
        # finish_at이 비어있으면, 생성일 기준으로 2주 뒤 자동 설정
        if not self.finish_at and self.created_at:
            self.finish_at = self.created_at + timedelta(weeks=2)
        super().save(*args, **kwargs)


    #투표 번호에 따른 항목 텍스트 필드 반환
    def get_option_text(self, choice_num):
        options = {1: self.option1, 2: self.option2, 3: self.option3}
        return options.get(choice_num, "")

    #모든 항목에 대한 투표 수 반환
    def count_votes(self):
        return {
            1: self.votes.filter(choice=1).count(),
            2: self.votes.filter(choice=2).count(),
            3: self.votes.filter(choice=3).count(),
        }

class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choices = [
        (1, 'Option 1'),
        (2, 'Option 2'),
        (3, 'Option 3'),
    ]
    choice = models.IntegerField(choices=choices)

    class Meta:
        # 한 유저는 한 게시글에 한 번만 투표
        unique_together = ('post', 'user')


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(null=True, blank=True)
    liked = models.ManyToManyField(User, related_name='liked_comment')
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def get_vote_choice(self):
        try:
            return Vote.objects.get(post=self.post, user=self.user).choice
        except Vote.DoesNotExist:
            return None

class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(null=True, blank=True)
    liked = models.ManyToManyField(User, related_name='liked_reply')  # 추천인 추가
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def get_vote_choice(self):
        try:
            return Vote.objects.get(post=self.comment.post, user=self.user).choice
        except Vote.DoesNotExist:
            return None

class CommentEvidence(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_evidence')
    keyword = models.CharField(max_length=100)
    evidence = models.URLField(max_length=500, blank=True, null=True)

class ReplyEvidence(models.Model):
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name='reply_evidence')
    keyword = models.CharField(max_length=100)
    evidence = models.URLField(max_length=500, blank=True, null=True)