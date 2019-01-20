#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.getcwd())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mymarketplace.settings")

import django
django.setup()

from marketplace.models import *


def setup_users():
    user01 = MarketplaceUser.objects.create_superuser(
        username="test01",
        email="test01@mymarketplace.com",
        password="01test"
    )

    user02 = MarketplaceUser.objects.create_user(
        username="test02",
        email="test02@mymarketplace.com",
        password="02test"
    )

    user01.save()
    user02.save()


def setup_products():
    products = [
        {
            "title": "Laptop",
            "price": 1000.42,
            "inventory_count": 20,
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
        },
        {
            "title": "Music album",
            "price": 20,
            "inventory_count": 100,
        },
        {
            "title": "Cool mug",
            "price": 100,
            "inventory_count": 1,
        },
    ]

    for product in products:
        new_product = Product.objects.create(
            title=product["title"],
            price=product["price"],
            inventory_count=product["inventory_count"]
        )
        new_product.save()


def run():
    print("Initializing database with dummy data...", end=" ")
    setup_users()
    setup_products()
    print("\033[1;32mDone\033[0m")


if __name__ == "__main__":
    run()
