from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError

# Create your models here.


class MarketplaceUser(AbstractUser):
    """This class represents a user model used in our marketplace. We are not
    really adding any new fields to AbstractUser for now, but this gives us the
    option to extend this model later on.
    """
    email = models.EmailField(unique=True, max_length=80)


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
    seller = models.ForeignKey(MarketplaceUser, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"Product: {self.title}, price: {self.price}. Amount in store: {self.inventory_count}"


class Cart(models.Model):
    """This class represents a cart model used in our marketplace. Each single
    cart is associated with a registered user of our website.

    Args:

    Attributes:
    """
    user = models.OneToOneField(MarketplaceUser, on_delete=models.CASCADE)
    item_count = models.PositiveIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

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

    def __str__(self):
        return f"Entry: {self.associated_cart.user}. Product: {self.product}, amount: {self.product_count}"


@receiver(post_save, sender=CartEntry)
def add_entry_to_cart(sender, instance, **kwargs):
    """Whenever a CartEntry instance is created, we update the information in
    the associated cart, i.e total item count, and total cost.

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if instance.product_count <= 0:
        raise ValidationError("Must add a valid amount.")
    # This is to avoid possible race condition. During the process of checking whether
    # a product is available. The product's true amount might have been decreased without
    # the controller process knowing.
    elif instance.product.inventory_count < 0:
        raise ValidationError("There are not enough items in inventory.")
    else:
        instance.associated_cart.total_cost += instance.cost
        instance.associated_cart.item_count += instance.product_count

        instance.associated_cart.save()


@receiver(pre_delete, sender=CartEntry)
def remove_entry_from_cart(sender, instance, **kwargs):
    """Whenever a CartEntry instance is removed, we update the information in
    the associated cart, i.e total item count, and total cost.

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    instance.associated_cart.total_cost -= instance.cost
    instance.associated_cart.item_count -= instance.product_count

    instance.associated_cart.save()
