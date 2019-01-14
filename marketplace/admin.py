from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *

# Register your models here.


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = MarketplaceUser
    list_display = ['email', 'username']


admin.site.register(MarketplaceUser, CustomUserAdmin)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartEntry)
