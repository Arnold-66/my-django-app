from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images', blank=True, null=True)
    video = models.FileField(upload_to='post_video', blank=True, null=True)
    views = models.PositiveIntegerField(default=0)  # Track number of views
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def total_likes(self):
        return self.likes.count()
    #def __str__(self):
       # return self.title
    def get_absolute_url(self):
        return reverse('blog:post-detail', kwargs={'pk': self.pk})
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    #likes = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name="liked_comments", blank=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title} - {self.likes.count()} Likes'

    

class Reply(models.Model):
    comment = models.ForeignKey('Comment', related_name='replies', on_delete=models.CASCADE)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    #likes = models.PositiveIntegerField(default=0)
    likes =  models.ManyToManyField(User, related_name="liked_replies", blank=True)


    def __str__(self):
        return f"Reply by {self.author} on {self.date_posted}"
    

class Announcement(models.Model):
    title = models.CharField(max_length=225)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    

class Event(models.Model):
    title = models.CharField(max_length=225)
    description = models.TextField()
    event_date = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=200)
    media = models.FileField( upload_to='events/', null=True, blank=True)  # Store image/video in 'events/' directory

    def __str__(self):
        return self.title