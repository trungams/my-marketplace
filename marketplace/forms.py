from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MarketplaceUser


class CustomUserCreationForm(UserCreationForm):
    """TODO

    """

    class Meta:
        model = MarketplaceUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    """TODO

    """

    class Meta:
        model = MarketplaceUser
        fields = ('username', 'email')
