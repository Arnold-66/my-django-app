from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
import logging
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile, Message
from blog.models import Post  # Import the Post model
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import requests
from django.db.models import Q
from django.urls import reverse_lazy


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user first
            Profile.objects.create(user=user)  # Create the associated Profile
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

logger = logging.getLogger(__name__)

def custom_logout(request):
    logger.debug("Custom logout called.")
    logout(request)  # This logs the user out
    messages.success(request, 'You have been logged out successfully.')
    return render(request, 'users/logout.html' )


class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully logged in!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('home')  # Redirect to home page after login

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'u_form': u_form, 'p_form': p_form})




def send_message(request, username):
    receiver = get_object_or_404(User, username=username)
    #return render(request, 'users/chat.html', {'username': receiver.username})
    return render(request, 'users/chat.html', {'receiver': receiver})

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)  # Ensure profile exists
    posts = Post.objects.filter(author=user).order_by('-date_posted')  # Get the user's posts

    context = {
        'profile': profile,
        'posts': posts
    }

    # Only show form if the logged-in user is viewing their own profile
    if request.user == user:
        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('users:user_profile', username=user.username)

        else:
            u_form = UserUpdateForm(instance=user)
            p_form = ProfileUpdateForm(instance=profile)

        context.update({'u_form': u_form, 'p_form': p_form})

    return render(request, 'users/user_profile.html', context)


@csrf_exempt
def update_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Check if the latitude and longitude are valid
        if latitude is None or longitude is None:
            return JsonResponse({"status": "failed", "message": "Latitude or longitude is missing."}, status=400)
        
        # Get the address from coordinates
        address = get_address_from_coordinates(latitude, longitude)

        if address is None:
            return JsonResponse({"status": "failed", "message": "Could not retrieve address."}, status=500)

        # Save the location data to the user's profile
        user_profile = Profile.objects.get(user=request.user)
        user_profile.location = address  # Save the location name
        user_profile.save()

        return JsonResponse({"status": "success", "address": address, "latitude": latitude, "longitude": longitude})

    return JsonResponse({"status": "failed"}, status=400)


def get_address_from_coordinates(latitude, longitude):
    api_key = '23debcd504e241df857f10b6ff325ef6'  # Replace with your actual API key
    url = f'https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={api_key}'
    
    try:
        response = requests.get(url)
        result = response.json()

        # Check if the response status is OK and results are returned
        if result['status']['code'] == 200 and len(result['results']) > 0:
            address = result['results'][0]['formatted']
            return address
        else:
            # If no results or error in response
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None



def chat_view(request, username):
    # Get the user we're chatting with
    receiver = get_object_or_404(User, username=username)

    # Fetch all messages between the logged-in user and the receiver
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('timestamp')

    # If the user submits a message, save it and reload the messages
    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=message_content
            )
            messages = Message.objects.filter(
                (Q(sender=request.user) & Q(receiver=receiver)) |
                (Q(sender=receiver) & Q(receiver=request.user))
            ).order_by('timestamp')

    # Get a list of users to display as options for chats
    users = User.objects.exclude(username=request.user.username)  # Exclude the current user

    return render(request, 'users/chat.html', {
        'username': username,
        'messages': messages,
        'users': users  # Pass a list of other users for the sidebar
    })