'''
There might be different pages on your site that display posts, but there is a
single URL that you use as the main URL for a post. Canonical URLs allow you to specify the URL for
the master copy of a page.
'''

from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager
class PublishedManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

class Post(models.Model):
    # the first model defined becomes the 
    # default model manager
    # You can use the Meta attribute
    # default_manager_name to specify a different default manager.
    objects=models.Manager()
    tags=TaggableManager()
    published=PublishedManager()
    class Status(models.TextChoices):
        DRAFT='DF','Draft'
        PUBLISHED='PB','Published'
    title=models.CharField(max_length=250,)
    # slug fields imply indexs by default so an index will be created
    slug=models.SlugField(max_length=250,unique_for_date='publish')
    body=models.TextField()
    publish=models.DateTimeField(default=timezone.now)
    # auto_now_add saves time as post is created
    created=models.DateTimeField(auto_now_add=True)
    # auto_now_add saves time every time post is updated
    updated=models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,
                choices=Status.choices,
                default=Status.DRAFT)
    # relation is many to one with user table and related_name allows 
    # us to access the field in the referenced table
    # foreign key fields imply indexs by default so an index will be created
    author=models.ForeignKey(User, on_delete=models.CASCADE,related_name='blog_posts')
    #saves metadata
    class Meta:
        # we are defininig the ordering to be in descending order "-"
        ordering = ["-publish"]

        #indexs values in table using publish field in descending order
        indexes = [
            models.Index(fields=['-publish']),
            ]
    def __str__(self) -> str:
        return self.title
    # this helps us to get the absolute path
    # for a particular resource
    def get_absolute_url(self):
        return reverse('blog:post_detail',
                        args=[self.publish.year,self.publish.month,self.publish.day,self.slug])


class Comment(models.Model):
    '''We can retrieve the post of a comment object using comment.post and
    retrieve all comments associated with a post object using post.comments.all(). If you don`t define
    the related_name attribute, Django will use the name of the model in lowercase, followed by _set
    (that is, comment_set) to name the relationship of the related object to the object of the model, where
    this relationship has been defined.'''
    post = models.ForeignKey(Post,
        on_delete=models.CASCADE,
        related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
            ]
    def __str__(self):
        return f'Comment by {self.name} on {self.post}'