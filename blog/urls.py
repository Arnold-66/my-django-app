from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, PostDeleteView, UserPostListView, CommentDeleteView, ReplyDeleteView
from . import views

app_name = 'users'
app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('user/<str:username>/posts/', UserPostListView.as_view(), name='user_posts'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user_posts'),
    path('add-post/', PostCreateView.as_view(), name='add_post'),
    path('delete-post/<int:pk>/', PostDeleteView.as_view(), name='delete_post'),
    #path('post/<int:post_id>/comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
    path('like-post/<int:post_id>/', views.like_post, name='like-post'),
    path('like-comment/<int:comment_id>/', views.like_comment, name='like-comment'),
    path('like-reply/<int:reply_id>/', views.like_reply, name='like-reply'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='delete-comment'),
    path('delete-reply/<int:pk>/', ReplyDeleteView.as_view(), name='delete-reply'),
    path('reply/delete/<int:pk>/', ReplyDeleteView.as_view(), name='delete-reply'),
    path('announcements_list/', views.announcements_list, name='announcements_list'),
    path('events_list/', views.events_list, name='events_list'),
    path("search/", views.search_results, name="search_results"),
    
    path('about/', views.about, name='blog-about'),
    path('latest_posts/', views.latest_posts, name='latest_posts')
]