from django import forms
from .models import ArticleComment, ArticleReply

class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = ArticleComment
        fields = ['content']
        labels = {
            'content': '댓글',
        }

class ArticleReplyForm(forms.ModelForm):
    class Meta:
        model = ArticleReply
        fields = ['content']
        labels = {
            'content': '답글',
        }
