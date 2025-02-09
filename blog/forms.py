from django import forms
from .models import Post, Comment, Reply, Event, Announcement

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'video']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'cols': 10, 'class': 'form-control'}),  # Smaller size
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'cols': 100, 'class': 'form-control'}),  # Smaller size
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']  # Specify the fields to be included
        widget = {
            'content': forms.Textarea(attrs={'rows': 3, 'cols': 30, 'class': 'form-control'}),  # Smaller size
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_date', 'location', 'media' ]
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content']