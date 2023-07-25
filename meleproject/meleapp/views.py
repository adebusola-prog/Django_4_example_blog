from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count


def post_list(request, tag_slug=None):
    posts=Post.published.all()
    tag= None
    if tag_slug:
        tag= get_object_or_404(Tag, slug=tag_slug)
        post_list= posts.filter(tags__in=[tag])

    # pagination with 3 posts per page
    paginator= Paginator(posts, 3)
    page_number=request.GET.get('page', 1)
    posts=paginator.page(page_number)
    return render(request, 'meleapp/list.html', {'posts':posts})

def post_detail(request, year, month, day, post):
    post=get_object_or_404(Post,
                           status=Post.Status.PUBLISHED,
                           slug=post,
                           publish__year=year,
                           publish__month=month,
                           publish__day=day)
    # List of active comments for this post
    comments=post.comments.filter(active=True) #comments in post.comments is the related name in the models
    # form for users to commit
    form = CommentForm()
    post_tags_ids=post.tags.values_list('id', flat=True)
    similar_posts= Post.published.filter(tags__in=post_tags_ids)\
                                .exclude(id=post.id)
    similar_posts=similar_posts.annotate(same_tags=Count('tags'))\
                                .order_by('-same_tags', '-publish')[:4]
    return render(request,
                  'meleapp/detail.html',
                  {'post':post, 'comments':comments, 'form':form,
                   'similar_posts': similar_posts
                   })

def post_share(request, post_id):
    # Retrieve post by id
    post=get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent=False

    if request.method == "POST":
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data  #helps to retrieve the validated data
            post_url=request.build_absolute_uri(post.get_absolute_url())
            subject=f"{cd['name']} recommends you read"\
                    f"{post.title}"
            message= f"Read{post.title} at {post_url}\n\n"\
                    f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'adebusolayeye@gmail.com',
                      [cd['to']])
            sent=True
    else:
        form= EmailPostForm()
    return render(request, 'meleapp/share.html', {'post':post,
                                                  'form':form,
                                 'sent':sent})

@require_POST
def post_comment(request, post_id):
    post=get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment=None
    form=CommentForm(data=request.POST)
    if form.is_valid():
        comment=form.save(commit=False)
        comment.post= post
        comment.name = request.user
        comment.save()
    return render(request, 'meleapp/comment.html', {'post':post, 'form':form, 'comment':comment})
