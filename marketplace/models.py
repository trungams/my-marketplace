from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.shortcuts import reverse
import warnings

from .exceptions import ProductNotAvailableException, ItemLeftInCartWarning

# Create your models here.


class MarketplaceUser(AbstractUser):
    """This class represents a user model used in our marketplace. We are not
    really adding any new fields to AbstractUser for now, but this gives us the
    option to extend this model later on.
    """
    email = models.EmailField(unique=True, max_length=80, blank=False)


class Product(models.Model):
    """This class represents a product model used in our marketplace. A product
    must have a name, price, and inventory count to indicate the available
    amount in our store.

    Args:

    Attributes:
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    inventory_count = models.IntegerField(default=0)
    category = models.CharField(max_length=100, default="miscellaneous", null=True, blank=True)
    description = models.TextField(default="", null=True, blank=True)
    seller = models.ForeignKey(MarketplaceUser, on_delete=models.CASCADE, default=None, null=True)

    def get_url_view_single_product(self):
        return reverse("marketplace:api_view_single_product", args=[str(self.id)])

    def get_url_add_to_cart(self):
        return reverse("marketplace:api_add_to_cart", args=[str(self.id)])

    def __str__(self):
        return f"Product: {self.title}, price: {self.price}. Amount in store: {self.inventory_count}"


class Cart(models.Model):
    """This class represents a cart model used in our marketplace. Each single
    cart is associated with a registered user of our website.

    Args:

    Attributes:
    """
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(MarketplaceUser, on_delete=models.CASCADE)
    item_count = models.PositiveIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @classmethod
    @transaction.atomic
    def checkout_cart(cls, pk):
        """TODO"""
        cart_entries = CartEntry.objects.select_for_update().filter(associated_cart__id=pk)
        item_left = False

        for entry in cart_entries:
            try:
                CartEntry.checkout_entry(entry.id)
            except ProductNotAvailableException:
                item_left = True

        if item_left:
            warnings.warn("There are items not checked out", ItemLeftInCartWarning)

    def __str__(self):
        return f"{self.user}'s cart. There are {self.item_count} items and total cost is {self.total_cost}"


class CartEntry(models.Model):
    """This class represents a single cart entry used in our marketplace.
    Each entry holds information about the associated cart, a product in store,
    and the product count. An entry cannot be added if the product is currently
    not available (not enough items, or product does not exist)

    Args:

    Attributes:
    """
    id = models.AutoField(primary_key=True)
    associated_cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_count = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = (('associated_cart', 'product'),)

    def save(self, *args, **kwargs):
        """TODO

        :param args:
        :param kwargs:
        :return:
        """
        self.cost = self._calculate_cost()
        return super().save(*args, **kwargs)

    def _calculate_cost(self):
        """TODO

        :return:
        """
        cost = self.product.price * self.product_count
        return cost

    @classmethod
    @transaction.atomic
    def checkout_entry(cls, pk):
        """TODO"""
        cart_entry = cls.objects.select_for_update().get(pk=pk)

        if cart_entry.product.inventory_count < cart_entry.product_count:
            raise ProductNotAvailableException("There are not enough items in inventory.")
        cart_entry.product.inventory_count -= cart_entry.product_count

        cart_entry.product.save()
        cart_entry.delete()

    def get_url_update_cart_entry(self):
        return reverse("marketplace:api_update_cart_entry", args=[str(self.id)])

    def get_url_checkout_cart_entry(self):
        return reverse("marketplace:api_checkout_cart_entry", args=[str(self.id)])

    def __str__(self):
        return f"Entry: {self.associated_cart.user}'s cart. Product: {self.product.title}, amount: {self.product_count}"


@receiver(post_save, sender=MarketplaceUser)
def create_default_cart_for_new_user(sender, instance, **kwargs):
    """TODO"""
    if instance:
        new_cart = Cart(user=instance)
        new_cart.save()


@receiver(pre_save, sender=CartEntry)
@transaction.atomic
def update_cart_entry(sender, instance, **kwargs):
    """If a cart entry information is updated, we should update the cart's info
    as well"""
    try:
        current_cart_entry = CartEntry.objects.select_for_update().get(pk=instance.id)

        prev_product_count = current_cart_entry.product_count
        prev_cost = current_cart_entry.cost

        instance.associated_cart.item_count -= prev_product_count
        instance.associated_cart.total_cost -= prev_cost

        instance.associated_cart.save()
    except CartEntry.DoesNotExist:
        pass


@receiver(post_save, sender=CartEntry)
@transaction.atomic
def add_entry_to_cart(sender, instance, **kwargs):
    """Whenever a CartEntry instance is created, we update the information in
    the associated cart, i.e total item count, and total cost."""

    # This is to avoid possible race condition. During the process of checking whether
    # a product is available. The product's true amount might have been decreased without
    # the controller process knowing.
    cart = Cart.objects.select_for_update().get(id=instance.associated_cart.id)

    if instance.product.inventory_count < 0:
        raise ProductNotAvailableException("There are not enough items in inventory.")
    else:
        cart.total_cost += instance.cost
        cart.item_count += instance.product_count

        cart.save()


@receiver(pre_delete, sender=CartEntry)
@transaction.atomic
def remove_entry_from_cart(sender, instance, **kwargs):
    """Whenever a CartEntry instance is removed, we update the information in
    the associated cart, i.e total item count, and total cost."""
    cart = Cart.objects.select_for_update().get(id=instance.associated_cart.id)

    cart.total_cost -= instance.cost
    cart.item_count -= instance.product_count

    cart.save()
