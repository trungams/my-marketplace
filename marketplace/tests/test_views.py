from django.test import TransactionTestCase, Client
from django.contrib import auth

from ..models import *


class UserAccountTestCase(TransactionTestCase):
    """Tester class for basic login/logout functions on our website"""
    def setUp(self):
        # Create two users, empty carts should to be there by default
        MarketplaceUser.objects.create_user(
            username="test01",
            email="test01@mymarketplace.com"
        )

        MarketplaceUser.objects.create_user(
            username="test02",
            email="test02@mymarketplace.com"
        )

        # Add some items to inventory
        products = [
            {
                "title": "Laptop",
                "price": 1000.42,
                "inventory_count": 0,
            },
            {
                "title": "Book",
                "price": 20.00,
                "inventory_count": 10000,
            },
            {
                "title": "Fountain pen",
                "price": 15,
                "inventory_count": 0,
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

    def test_user_login_and_logout(self):
        """Check basic login/logout flow"""
        # Check if it's possible to get the login page
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

        test01_user = MarketplaceUser.objects.get(username="test01")

        # Logs in the user
        self.client.force_login(test01_user)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        # User will be redirected from login page
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("marketplace:index"))

        # Logs out the current user
        self.client.logout()
        # User will be able to access login page again
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        # User is logged out
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

        # Logs in again to ensure there is no error
        self.client.force_login(test01_user)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        # Logged in users should not be able to access register page
        response = self.client.get(reverse("register"))
        self.assertRedirects(response, reverse("marketplace:index"))


class MarketplaceClient(Client):
    """A subclass for Client to deal with HTTP request methods more easily"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MarketplaceViewTestCase(TransactionTestCase):
    """Tester class for any logic error and vulnerability in our views implementation"""
    client_class = MarketplaceClient

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = MarketplaceClient()

    def setUp(self):
        # Create two users, empty carts should to be there by default
        MarketplaceUser.objects.create_user(
            username="test01",
            email="test01@mymarketplace.com"
        )

        MarketplaceUser.objects.create_user(
            username="test02",
            email="test02@mymarketplace.com"
        )

        # Add some items to inventory
        products = [
            {
                "title": "Laptop",
                "price": 1000.42,
                "inventory_count": 0,
            },
            {
                "title": "Book",
                "price": 20.00,
                "inventory_count": 10000,
            },
            {
                "title": "Fountain pen",
                "price": 15,
                "inventory_count": 0,
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

        # We're only testing with logged in users for now
        test01_user = MarketplaceUser.objects.get(username="test01")
        self.client.force_login(test01_user)

        self.http_request_functions = {
            "GET": self.client.get,
            "POST": self.client.post,
            "HEAD": self.client.head,
            "TRACE": self.client.trace,
            "OPTIONS": self.client.options,
            "PUT": self.client.put,
            "PATCH": self.client.patch,
            "DELETE": self.client.delete
        }

        try:
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

    def test_view_index(self):
        """Tests for index page"""
        url = reverse("marketplace:index")
        allowed_http_methods = ["GET", "POST", "HEAD", "TRACE", "OPTIONS", "PUT", "PATCH", "DELETE"]

        self._check_http_allowed(url, allowed_http_methods)

    def test_view_register(self):
        """Tests for account registration page"""
        url = reverse("register")
        allowed_http_methods = ["HEAD", "GET", "POST"]
        forbidden_http_methods = ["TRACE", "OPTIONS", "PUT", "PATCH", "DELETE"]

        # This is to avoid redirection when our client is already logged in
        self.client.logout()

        self._check_http_not_allowed(url, forbidden_http_methods)
        self._check_http_allowed(url, allowed_http_methods)

    def test_view_api_retrieve_products(self):
        """Tests for api_retrieve_products view"""
        url = reverse("marketplace:api_view_products")
        allowed_http_methods = ["HEAD", "GET"]
        forbidden_http_methods = ["POST", "TRACE", "OPTIONS", "PUT", "PATCH", "DELETE"]

        self._check_http_not_allowed(url, forbidden_http_methods)
        self._check_http_allowed(url, allowed_http_methods)

    def test_view_api_retrieve_single_product(self):
        """Tests for api_retrieve_single_product view"""
        url = reverse("marketplace:api_view_single_product", args=["1"])
        allowed_http_methods = ["HEAD", "GET"]
        forbidden_http_methods = ["POST", "TRACE", "OPTIONS", "PUT", "PATCH", "DELETE"]

        self._check_http_not_allowed(url, forbidden_http_methods)
        self._check_http_allowed(url, allowed_http_methods)

    def test_view_api_retrieve_cart(self):
        """Tests for api_retrieve_cart view"""
        url = reverse("marketplace:api_view_cart")
        allowed_http_methods = ["HEAD", "GET"]
        forbidden_http_methods = ["POST", "TRACE", "OPTIONS", "PUT", "PATCH", "DELETE"]

        self._check_http_not_allowed(url, forbidden_http_methods)
        self._check_http_allowed(url, allowed_http_methods)

    def test_view_api_add_to_cart(self):
        """Tests for api_add_to_cart view"""
        url = reverse("marketplace:api_add_to_cart", args=["1"])
        allowed_http_methods = ["HEAD", "GET", "POST"]
        forbidden_http_methods = ["TRACE", "OPTIONS", "PUT", "PATCH", "DELETE"]

        self._check_http_not_allowed(url, forbidden_http_methods)
        self._check_http_allowed(url, allowed_http_methods)

    def test_view_api_update_cart_entry(self):
        """Tests for api_update_cart_entry view"""
        url = reverse("marketplace:api_update_cart_entry", args=["1"])
        allowed_http_methods = ["HEAD", "GET", "POST"]
        forbidden_http_methods = ["TRACE", "OPTIONS", "PUT", "PATCH", "DELETE"]

        self._check_http_not_allowed(url, forbidden_http_methods)
        self._check_http_allowed(url, allowed_http_methods)

    def test_view_api_checkout_product(self):
        """Tests for api_checkout_product view"""
        url = reverse("marketplace:api_checkout_product", args=["1"])
        allowed_http_methods = ["POST"]
        forbidden_http_methods = ["HEAD", "GET", "TRACE", "OPTIONS", "PUT", "PATCH", "DELETE"]

        self._check_http_not_allowed(url, forbidden_http_methods)
        self._check_http_allowed(url, allowed_http_methods)

    def test_view_api_checkout_cart_entry(self):
        """Tests for api_checkout_cart_entry view"""
        url = reverse("marketplace:api_checkout_cart_entry", args=["1"])
        allowed_http_methods = ["POST"]
        forbidden_http_methods = ["HEAD", "GET", "TRACE", "OPTIONS", "PUT", "PATCH", "DELETE"]

        self._check_http_not_allowed(url, forbidden_http_methods)
        self._check_http_allowed(url, allowed_http_methods)

    def test_api_checkout_cart(self):
        """Tests for api_checkout_cart view"""
        url = reverse("marketplace:api_checkout_cart")
        allowed_http_methods = ["POST"]
        forbidden_http_methods = ["HEAD", "GET", "TRACE", "OPTIONS", "PUT", "PATCH", "DELETE"]

        self._check_http_not_allowed(url, forbidden_http_methods)
        self._check_http_allowed(url, allowed_http_methods)

    def _check_http_not_allowed(self, target_url, forbidden_http_methods):
        """This method iterates over a list of HTTP methods and verifies if a
        request to the target URL returns a status code of 403"""
        for method in forbidden_http_methods:
            http_request_function = self.http_request_functions[method]
            response = http_request_function(target_url)
            if response.status_code != 404:
                self.assertEqual(response.status_code, 405)

    def _check_http_allowed(self, target_url, allowed_http_methods):
        """This method iterates over a list of HTTP methods and verifies if a
        request to the target URL returns a status code different from 403"""
        for method in allowed_http_methods:
            http_request_function = self.http_request_functions[method]
            response = http_request_function(target_url)
            if response.status_code != 404:
                self.assertNotEqual(response.status_code, 405)
