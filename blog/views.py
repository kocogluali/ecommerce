from django.shortcuts import render
from .models import *
from comment.models import BlogComments
from django.contrib import messages
from django.shortcuts import get_object_or_404, get_list_or_404


def blogList(request, category="all"):
    if category == "all":
        post = get_list_or_404(Post, active=True, category__active=True)
    else:
        postCategory = get_object_or_404(PostCategory, active=True, slug=category)
        post = Post.objects.filter(active=True, category__active=True, category=postCategory)
        # post = Post.objects.filter(active=True,category__active=True,category__slug=category)
    context = {
        'cats': PostCategory.objects.filter(active=True).order_by("-id"),
        'posts': post,
        'category': category,
    }
    return render(request, "site/blog/blogList.html", context)


def blogDetail(request, category, post):
    blog = get_object_or_404(Post, slug=post, category__slug=category)
    try:
        next = blog.get_next_by_publishing_date()
    except:
        next = None
    try:
        prev = blog.get_previous_by_publishing_date()
    except:
        prev = None
    if request.method == "POST":
        if request.user.is_authenticated:
            eklendi = BlogComments.addComment(BlogComments, request.user, blog, request.POST.get("comment"))
            if eklendi:
                messages.add_message(request, messages.SUCCESS, "Yorum eklendi yönetici onayından sonra burada görebilirsin")
            else:
                messages.error(request, "Yorum eklenemedi")
        else:
            messages.error(request, "Yorum yapmak için giriş yapmalısın")

    context = {
        'cats': PostCategory.objects.filter(active=True).order_by("-id"),
        'post': blog,
        'prev': prev,
        'next': next,
        'postComment': BlogComments.get_active_comments(BlogComments)
    }
    return render(request, "site/blog/blogDetail.html", context)
