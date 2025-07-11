from django.db import models
from accounts.models import User

class Article(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='articles/', null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    liked = models.ManyToManyField(User, related_name='liked_articles', blank=True)
    scrapped = models.ManyToManyField(User, related_name='scrapped_article_posts', blank=True)

    def __str__(self):
        return self.title

    def comment_count(self):
        return self.comments.count()

class ArticleSection(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='sections')
    heading = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='articles/sections/', null=True, blank=True)
    image_alt = models.CharField(max_length=200, blank=True)
    quote = models.CharField(max_length=300, blank=True)
    text = models.TextField()

    def __str__(self):
        return f"{self.article.title} - {self.heading}"

class AuthorProfile(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='author_profile')
    name = models.CharField(max_length=50)
    role = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to='authors/', null=True, blank=True)

    def __str__(self):
        return self.name

class ArticleComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='article_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    liked = models.ManyToManyField(User, related_name='liked_article_comment')

class ArticleReply(models.Model):
    comment = models.ForeignKey(ArticleComment, on_delete=models.CASCADE, related_name='article_replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    liked = models.ManyToManyField(User, related_name='liked_article_reply') 

class ArticleCommentEvidence(models.Model):
    comment = models.ForeignKey(ArticleComment, on_delete=models.CASCADE, related_name='article_comment_evidence')
    keyword = models.CharField(max_length=100)
    link1 = models.URLField(max_length=500, blank=True, null=True)
    link2 = models.URLField(max_length=500, blank=True, null=True)
    link3 = models.URLField(max_length=500, blank=True, null=True)
    link4 = models.URLField(max_length=500, blank=True, null=True)

class ArticleReplyEvidence(models.Model):
    reply = models.ForeignKey(ArticleReply, on_delete=models.CASCADE, related_name='article_reply_evidence')
    keyword = models.CharField(max_length=100)
    link1 = models.URLField(max_length=500, blank=True, null=True)
    link2 = models.URLField(max_length=500, blank=True, null=True)
    link3 = models.URLField(max_length=500, blank=True, null=True)
    link4 = models.URLField(max_length=500, blank=True, null=True)
