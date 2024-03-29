from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import MarketplaceUser, Product, CartEntry


class CustomUserCreationForm(UserCreationForm):
    """Form class to create new accounts on our website"""
    class Meta:
        model = MarketplaceUser
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    """Form class to update current users of our website"""
    class Meta:
        model = MarketplaceUser
        fields = ("username", "email")


class ProductAddForm(forms.ModelForm):
    """Form class to add new products to the marketplace

    Not implemented"""
    class Meta:
        model = Product
        fields = ("title", "price", "inventory_count", "category", "description", "seller")


class ProductEditForm(forms.ModelForm):
    """Form class to modify product inventory on the marketplace

    Not implemented"""
    pass


class CartEntryAddForm(forms.ModelForm):
    """Form class to add a product to personal cart"""
    product_count = forms.IntegerField(min_value=0)

    class Meta:
        model = CartEntry
        fields = ("product_count",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product_count"].initial = 1
        print(self)

    def clean_product_count(self):
        """Validates data before saving form values"""
        data = self.cleaned_data["product_count"]

        # In addition to checking whether the amount added to cart is valid, we should also
        # check for product's availability. But it should be done in the caller
        if data <= 0:
            raise ValidationError("Must add a valid amount to cart.")

        return data


class CartEntryUpdateForm(forms.ModelForm):
    """Form class to update a cart entry"""
    product_count = forms.IntegerField(min_value=0)

    class Meta:
        model = CartEntry
        fields = ("product_count",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance:
            self.fields["product_count"].initial = instance.product_count

    def clean_product_count(self):
        """Similar to creating cart entry, we do not allow invalid parameters
        to be passed in this form."""
        data = self.cleaned_data["product_count"]

        if data <= 0:
            raise ValidationError("Must be a valid amount.")

        return data
