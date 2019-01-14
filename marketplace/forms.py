from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import MarketplaceUser, Product, CartEntry


class CustomUserCreationForm(UserCreationForm):
    """TODO

    """

    class Meta:
        model = MarketplaceUser
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    """TODO

    """

    class Meta:
        model = MarketplaceUser
        fields = ("username", "email")


class ProductAddForm(forms.ModelForm):
    """TODO"""
    class Meta:
        model = Product
        fields = ("title", "price", "inventory_count", "category", "description", "seller")


class ProductEditForm(forms.ModelForm):
    """TODO"""
    pass


class CartEntryAddForm(forms.ModelForm):
    """TODO"""
    product_count = forms.IntegerField(min_value=0)

    class Meta:
        model = CartEntry
        fields = ("product_count",)

    def clean_product_count(self):
        data = self.cleaned_data["product_count"]

        # In addition to checking whether the amount added to cart is valid, we should also
        # check for product's availability. But it should be done in the caller
        if data <= 0:
            raise ValidationError("Must add a valid amount to cart.")

        return data


class CartEntryUpdateForm(forms.ModelForm):
    """TODO"""
    pass
