from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomLoginView
from . import views

app_name  = 'blog'
app_name = 'users'

urlpatterns = [

    path('profile/<str:username>/', views.user_profile, name='user_profile'),  # Other users' profiles
    path('message/<str:username>/', views.send_message, name='send_message'),  # Ensure this line exists
    path('update_location/', views.update_location, name='update_location'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
     path('login/', CustomLoginView.as_view(), name='login'),  
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('chat/<str:username>/', views.chat_view, name='chat_view'),  # This is the key line
]
    

