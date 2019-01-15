from django.test import TestCase

from ..models import *


class MarketplaceModelsTestCase(TestCase):
    """Since all of our models are referring to each other, it would make more
    sense to include them in one test class
    """
    @classmethod
    def setUpTestData(cls):
        # Create a single user, an empty cart should to be there by default
        test01_user = MarketplaceUser.objects.create_user(
            username="test01",
            email="test01@mymarketplace.com"
        )

        test02_user = MarketplaceUser.objects.create_user(
            username="test02",
            email="test02@mymarketplace.com"
        )

    def setUp(self):
        try:
            # Add some items to inventory
            products = [
                {
                    "title": "Laptop",
                    "price": 1000.42,
                    "inventory_count": 100,
                },
                {
                    "title": "Book",
                    "price": 20.00,
                    "inventory_count": 10000,
                },
                {
                    "title": "Fountain pen",
                    "price": 15,
                    "inventory_count": 200,
                },
                {
                    "title": "Candy",
                    "price": 0.10,
                    "inventory_count": 10,
                }
            ]

            for product in products:
                Product.objects.create(
                    title=product["title"],
                    price=product["price"],
                    inventory_count=product["inventory_count"]
                )

            laptop = Product.objects.get(title="Laptop")
            book = Product.objects.get(title="Book")
            fountain_pen = Product.objects.get(title="Fountain pen")
            candy = Product.objects.get(title="Candy")

            # Get the 2 carts corresponding to 2 new user
            test_01_associated_cart = Cart.objects.get(user__username="test01")
            test_02_associated_cart = Cart.objects.get(user__username="test02")

            # Initializing cart entries
            cart_entries = [
                {
                    "associated_cart": test_01_associated_cart,
                    "product": laptop,
                    "product_count": 1
                },
                {
                    "associated_cart": test_02_associated_cart,
                    "product": candy,
                    "product_count": 10,
                },
                {
                    "associated_cart": test_01_associated_cart,
                    "product": candy,
                    "product_count": 5,
                },
                {
                    "associated_cart": test_02_associated_cart,
                    "product": book,
                    "product_count": 3,
                },
                {
                    "associated_cart": test_02_associated_cart,
                    "product": fountain_pen,
                    "product_count": 2,
                }
            ]

            for entry in cart_entries:
                CartEntry.objects.create(
                    associated_cart=entry["associated_cart"],
                    product=entry["product"],
                    product_count=entry["product_count"]
                )
        except Exception:
            self.fail()

    def test_default_cart_created_for_new_user(self):
        """Check that a new user has a new cart created by default"""
        new_user = MarketplaceUser.objects.get(pk=1)
        self.assertTrue(Cart.objects.filter(user=new_user).exists(), True)

    def test_get_url_view_single_product(self):
        """Check that the URL to view a single product is correct"""
        product = Product.objects.get(id=1)
        self.assertEqual(
            product.get_url_view_single_product(),
            "/marketplace/api/products/1/view"
        )

    def test_get_url_add_to_cart(self):
        """Check that the URL to add a product to cart is correct"""
        product = Product.objects.get(id=1)
        self.assertEqual(
            product.get_url_add_to_cart(),
            "/marketplace/api/products/1/add-to-cart"
        )

    def test_get_url_update_cart_entry(self):
        """Check that the URL to update a cart entry is correct"""
        cart_entry = CartEntry.objects.get(id=1)
        self.assertEqual(
            cart_entry.get_url_update_cart_entry(),
            "/marketplace/api/cart/1/update"
        )

    def test_get_url_checkout_cart_entry(self):
        """Check that the URL to checkout a cart entry is correct"""
        cart_entry = CartEntry.objects.get(id=1)
        self.assertEqual(
            cart_entry.get_url_checkout_cart_entry(),
            "/marketplace/api/cart/1/checkout"
        )

    def test_marketplace_user_string_correct(self):
        """Check that user.__str__() returns what we expect"""
        user = MarketplaceUser.objects.get(id=1)
        expected_username = "test01"
        self.assertEqual(str(user), expected_username)

    def test_product_string_correct(self):
        """Check that product.__str__() returns what we expect"""
        product = Product.objects.get(id=1)
        expected_product_string = "Product: Laptop, price: 1000.42. Amount in store: 100"
        self.assertEqual(str(product), expected_product_string)

    def test_cart_string_correct(self):
        """Check that cart.__str__() returns what we expect"""
        cart = Cart.objects.get(id=1)
        expected_cart_string = "test01's cart. There are 6 items and total cost is 1000.92"
        self.assertEqual(str(cart), expected_cart_string)

    def test_cart_entry_string_correct(self):
        """Check that cart_entry.__str__() returns what we expect"""
        cart_entry = CartEntry.objects.get(id=1)
        expected_cart_entry_string = "Entry: test01's cart. Product: Laptop, amount: 1"
        self.assertEqual(str(cart_entry), expected_cart_entry_string)
