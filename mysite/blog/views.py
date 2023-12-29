from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.http import Http404
from .models import Post,Comment
from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm,SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector,SearchQuery,SearchRank
from django.contrib.postgres.search import TrigramSimilarity
# ...
# Create your views here.
# we use the require post decorator to
# for the view to accept only post requests
# Django will throw an HTTP 405 (method not allowed) error if you try to access the view with
# any other HTTP method.
def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector=SearchVector('title', weight='A')+SearchVector("body",weight='B')
            search_query=SearchQuery(query)
            # triagram checks how many consecutive three words 
            # the results share
            # results=Post.published.annotate(
            #     trigram=TrigramSimilarity('title',query)
            # ).filter(trigram__gte=0.1).order_by('-triagram')
            results = Post.published.annotate(
                search=search_vector,rank=SearchRank(search_vector,search_query)
                ).filter(rank__gte=0.3).order_by('-rank')
    return render(request,
        'blog/post/search.html',
        {'form': form,
        'query': query,
        'results': results})
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(request, 'blog/post/comment.html',
                    {'post': post,
                    'form': form,
                    'comment': comment})
def post_share(request,post_id):
    post = get_object_or_404(Post,id=post_id,status=Post.Status.PUBLISHED)
    sent=False
    if request.method == "POST":
        form=EmailPostForm(request.POST)        
        if form.is_valid():
            cd = form.cleaned_data
            post_url=request.build_absolute_uri(post.get_absolute_url())
            subject=f"{cd['name']} recommends you read " \
                f"{post.title}"
            message=f"Read {post.title} at {post_url}\n\n" \
                f"{cd['name']}\'s comments: {cd['comment']}"
            send_mail(subject,message,"abdissadegefu1@gmail.com",[cd["to"]])
            sent=True
    else:
        form=EmailPostForm()
    return render(request,"blog/post/share.html", {"form":form,"post":post,"sent":sent})
def post_list(request,tag_slug=None):
    posts=Post.published.all()
    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag,slug=tag_slug)
        posts=posts.filter(tags__in=[tag])
    paginator=Paginator(posts,3)
    page_number=request.GET.get("page",1)
    try:
        posts=paginator.page(page_number)
    except PageNotAnInteger:
        posts=paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)
    return render(request,'blog/post/list.html',{'posts':posts,'tag':tag})
class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
def post_detail(request,year,month,day,post):
    post=get_object_or_404(Post,status=Post.Status.PUBLISHED,slug=post,publish__year=year,publish__month=month,publish__day=day,)
    comments=post.comments.filter(active=True)
    form=CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
    .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
    .order_by('-same_tags','-publish')[:4]
    # try:
    #     post=Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("No Post Found.")
    return render (request,"blog/post/detail.html",{"post":post,"comments":comments,"form":form,"similar_posts":similar_posts})