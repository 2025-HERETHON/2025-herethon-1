from django.contrib import admin
from .models import Article, ArticleSection, AuthorProfile

admin.site.register(Article)
admin.site.register(ArticleSection)
admin.site.register(AuthorProfile)