from django.urls import path
from .views import AuthLoginView, logout_view, register_view, profile_view, profile_edit_view

app_name = 'Authen'

urlpatterns = [
    path('login/', AuthLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
]
