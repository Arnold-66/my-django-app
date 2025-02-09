from django.contrib import admin
from .models import Post, Comment, Announcement, Event, Reply

# Create an inline admin interface for the Comment model
class CommentInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = Comment
    extra = 1  # Number of empty comment forms to display by default

# Create an inline admin interface for the Reply model
class ReplyInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = Reply
    extra = 1

# Register the Post model with the CommentInline
class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInline]  # This adds the Comment section inside Post
    list_display = ('title', 'author', 'date_posted')  # Customize the list view of Post

class CommentAdmin(admin.ModelAdmin):
    inlines = [ReplyInline]  # Replies are shown inline within the comment

# Register your models with the admin site
admin.site.register(Comment, CommentAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Announcement)
admin.site.register(Event)
admin.site.register(Reply)
