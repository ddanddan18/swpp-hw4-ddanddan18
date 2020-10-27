from django.contrib import admin
from django.contrib.auth.models import User
from .models import Comment, Article

# Register your models here.
admin.site.register(Article)
admin.site.register(Comment)
