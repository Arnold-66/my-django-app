from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Post, Comment, Announcement, Event, Reply
from .forms import PostForm, CommentForm, ReplyForm, EventForm, AnnouncementForm
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib import messages
from django.http import request, JsonResponse
from django.db.models import F
from django.core.paginator import Paginator


def home(request):
    # Add a login success message if the user is authenticated
    if request.user.is_authenticated:
        messages.success(request, 'You have logged in successfully.')
    
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context, {})

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 5  # Number of posts per page
    ordering = ['-date_posted']


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = Post.objects.order_by('-date_posted')[:5]
        context['announcements'] = Announcement.objects.order_by('-created_at')[:3]
        context['events'] = Event.objects.order_by('-event_date')[:3]
        return context
    
    




@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    likes_count = post.likes.count()
    #print(f"Post {post_id} likes count: {likes_count}")  # Debugging line

    
    return JsonResponse({'liked': liked, 'likes_count': likes_count})
    

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user in comment.likes.all():
        comment.likes.remove(request.user)  # Unlike the comment
        liked = False
    else:
        comment.likes.add(request.user)  # Like the comment
        liked = True

    likes_count = comment.likes.count()  # Count the total likes

    return JsonResponse({'liked': liked, 'likes_count': likes_count})

@login_required
def like_reply(request, reply_id):
    if request.method == 'POST':
        reply = get_object_or_404(Reply, id=reply_id)
        if request.user in reply.likes.all():
            reply.likes.remove(request.user)
            liked = False
        else:
            reply.likes.add(request.user)
            liked = True
        
        likes_count = reply.likes.count()
        print(f"Comment{reply_id} likes count: {likes_count}")

        return JsonResponse({'liked': liked, 'likes_count':likes_count})


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post-detail.html"
    context_object_name = "post"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ensure post exists before fetching comments
        post = self.get_object()
        
        # Fetch comments related to the post (newest first) and prefetch replies for efficiency
        comments = post.comments.prefetch_related('replies').order_by("-date_posted")

        # Order replies under each comment by newest first
        for comment in comments:
            comment.sorted_replies = comment.replies.all().order_by('-date_posted')

        # Add necessary context data
        context['comments'] = comments
        context['replies'] = [reply for comment in comments for reply in comment.replies.all()]
        context["comment_form"] = CommentForm()
        context["reply_form"] = ReplyForm()
        context['total_likes'] = post.likes.count()

        return context
    # for the post views
    def get_object(self):
        post = super().get_object()
        user = self.request.user

        url = reverse('blog:post-detail', kwargs={'pk': post.pk})
        # Only increment views if the user is authenticated and hasn't viewed before
        if user.is_authenticated:
            if not self.request.session.get(f'viewed_post_{post.id}', False):
                post.views = F('views') + 1  # Increment views in the database safely
                post.save(update_fields=['views'])
                self.request.session[f'viewed_post_{post.id}'] = True  # Mark post as viewed in session

        return post

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        comment_id = request.POST.get("comment_id")  # ✅ Get the related comment ID

        if comment_id:  # If this is a reply
            comment = get_object_or_404(Comment, id=comment_id)  # ✅ Handle missing comment safely
            form = ReplyForm(request.POST)
            if form.is_valid():
                reply = form.save(commit=False)
                reply.comment = comment  # ✅ Link to the correct comment
                reply.author = request.user
                reply.save()
                messages.success(request, "Your reply has been posted!")
                return redirect(self.object.get_absolute_url())

        else:  # Otherwise, this is a comment
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = self.object
                comment.author = request.user
                comment.save()
                messages.success(request, "Your comment has been posted!")
                return redirect(self.object.get_absolute_url())

        return self.render_to_response(self.get_context_data(comment_form=form))




class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/add_post.html'
    success_url = reverse_lazy('blog:blog-home')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_additional_context(self):
        return {
            'latest_posts': Post.objects.order_by('-date_posted')[:5],
            'announcements': Announcement.objects.order_by('-created_at')[:3],
            'events': Event.objects.order_by('-event_date')[:3],
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_additional_context())
        return context

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/delete_post.html'
    success_url = reverse_lazy('blog:blog-home')
    
    def post(self, request, pk):
        post = get_object_or_404(post, pk=pk)

        if post.author == request.user:
            post.delete()
            messages.success(request, 'Your post has been deleted successfully!')

        return redirect('blog:post-detail', pk=post.pk)
    
    def get_success_url(self):
        post = self.object.post
        url = reverse('blog:post-detail', kwargs={'pk': post.pk})
        if post:
            return reverse('blog:post-detail', kwargs={'pk': post.pk})
        return reverse('home')  # Fallback if no associated post


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/delete-comment.html'
    def post(self, request, pk):
        # Retrieve the comment by primary key
        comment = get_object_or_404(Comment, pk=pk)
        
        # Only allow deletion if the comment's author matches the logged-in user
        if comment.author == request.user:
            comment.delete()
            messages.success(request, 'Your Comment deleted Successfully!')
        
        # Redirect to the post's detail page
        return redirect('blog:post-detail', pk=comment.post.pk)

    def get_success_url(self):
        post = self.object.post
        url = reverse('blog:post-detail', kwargs={'pk': post.pk})
        if post:
            return reverse('blog:post-detail', kwargs={'pk': post.pk})
        return reverse('home')  # Fallback if no associated post

    def get_queryset(self):
        # Ensure that only the comment's author can delete the comment
        return Comment.objects.filter(author=self.request.user)
    

class ReplyDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # Retrieve the comment by primary key
        reply = get_object_or_404(Reply, pk=pk)
        
        # Only allow deletion if the comment's author matches the logged-in user
        if reply.author == request.user:
            reply.delete()
            messages.success(request, 'Your Reply deleted Successfully!')
        
        # Redirect to the post's detail page
        return redirect('blog:post-detail', pk=reply.comment.post.pk)

    def get_success_url(self):
        post = self.object.post
        url = reverse('blog:post-detail', kwargs={'pk': post.pk})
        if post:
            return reverse('blog:post-detail', kwargs={'pk': post.pk})
        return reverse('home')  # Fallback if no associated post

    def get_queryset(self):
        # Ensure that only the comment's author can delete the comment
        return Reply.objects.filter(author=self.request.user)




class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

    def get_additional_context(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return {
            'user': user,
            'post_count': Post.objects.filter(author=user).count(),
            'latest_posts': Post.objects.order_by('-date_posted')[:5],
            'announcements': Announcement.objects.order_by('-created_at')[:3],
            'events': Event.objects.order_by('-event_date')[:3],
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_additional_context())
        return context


def share_post(request, post_id):
    post_url = request.build_absolute_uri(reverse("blog:post-detail", args=[post_id]))
    return redirect(post_url)

def announcements_list(request):
    if request.method == 'POST':
        a_form = AnnouncementForm(request.POST)
        if a_form.is_valid():
            a_form.save()
        return redirect('blog:announcements_list')
    else:
        a_form = AnnouncementForm()
        
    announcements = Announcement.objects.order_by('-created_at')
    return render(request, 'blog/announcements_list.html',  {'announcements': announcements, 'a_form': a_form })



def events_list(request):
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES)
        if event_form.is_valid():
            event_form.save()
            messages.success(request, 'Event Created Successfully!')
            return redirect('blog:events_list')  # Redirect after POST to avoid form resubmission
    else:
        event_form = EventForm()

    events = Event.objects.order_by('-event_date')

    # Loop through each event to check the media field
    for event in events:
        if event.media:
            # Ensure media exists and is accessible
            try:
                # This will raise an error if the URL is not valid or if the file is missing
                event.media.url
            except ValueError:
                # Handle the case where the file does not exist
                event.media = None

    return render(request, 'blog/events_list.html', {'events': events, 'event_form': event_form })


def latest_posts(request):
    latest_posts = Post.objects.order_by('-date_posted')[:5]
    for post in latest_posts:
        content_word_count = len(post.content.split())
        reading_time = round(content_word_count / 200)
        post.reading_time = reading_time

    context = {
        'latest_posts': latest_posts
    }
    return render(request, 'blog/latest_posts.html', context)


# handles search queries 
def search_results(request):
    query = request.GET.get("q", "")
    results = {"users": [], "posts": []}

    if query:
        # Search users by username
        users = User.objects.filter(username__icontains=query)

        # Search blog posts by title or content
        posts = Post.objects.filter(title__icontains=query) | Post.objects.filter(content__icontains=query)

        # ✅ Fetch all posts from found users (to show their blog posts)
        user_posts = {user: Post.objects.filter(author=user) for user in users}

        results = {"users": users, "posts": posts, "user_posts": user_posts}

    return render(request, "blog/search_results.html", {"query": query, "results": results})


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
