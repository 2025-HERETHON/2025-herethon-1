from django import forms
from proposals.models import ProposalComment, ProposalReply

class ProposalCommentForm(forms.ModelForm):
    class Meta:
        model = ProposalComment
        fields = ['title', 'problem', 'solution', 'effect']
        labels = {
            'title': '제안 제목',
            'problem': '현황 및 문제점',
            'solution': '개선 방안',
            'effect': '기대효과',
        }

class ProposalReplyForm(forms.ModelForm):
    class Meta:
        model = ProposalReply
        fields = ['content']
        labels = {
            'content' : '답글',
        }