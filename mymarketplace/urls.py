"""mymarketplace URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
# from django.views.generic.edit import CreateView
from django.contrib.auth import views as auth_views

# from marketplace.forms import CustomUserCreationForm
from marketplace.views import register

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='marketplace:index'), name='index'),
    path(
        'login',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            redirect_field_name='index',
            redirect_authenticated_user=True
        ),
        name='login'
    ),
    path('register', register, name='register'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
    path('marketplace/', include('marketplace.urls'))
]
