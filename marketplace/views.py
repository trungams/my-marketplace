from django.shortcuts import render, redirect, get_object_or_404
from django.http import (
    HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden, JsonResponse
)
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError

from .models import *
from .forms import *

# Create your views here.


def index(request):
    """Returns the index page with sitemap"""
    return render(request, "marketplace/index.html")


def register(request):
    """Let user register a new account on our website.

    Supported HTTP methods: GET, POST
    """

    if request.user.is_authenticated:
        # Registered users don't need to access this page
        return redirect("index")
    if request.method == "GET":
        form = CustomUserCreationForm()
        return render(request, "registration/register.html", {"form": form})
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        # Returns to register site in case of error
        return redirect("register")
    else:
        return HttpResponseNotAllowed(request)


def api_retrieve_products(request):
    """Let users view and search for products from our marketplace.

    Supported HTTP methods: GET

    Supported GET parameters:
        product: Search based on products' title
        category: Search based on products' category
        availability (true/false): Search based on products' availability
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(request)
    else:
        ctx = {}

        product_name = request.GET.get("product", "")
        category = request.GET.get("category", "")
        show_available = request.GET.get("availability", "false").lower()

        # if availability == true is GET request, show products in stock
        if show_available == "true":
            lower_bound = 0
        else:
            lower_bound = -1

        products_list = Product.objects.values(
            "id",
            "title",
            "price",
            "inventory_count",
            "category",
            "description",
            "seller__username"
        ).filter(
            inventory_count__gt=lower_bound,
            title__icontains=product_name,
            category__icontains=category
        ).order_by("title")

        ctx["products"] = list(products_list)

        return JsonResponse(ctx)


def api_retrieve_single_product(request, pk):
    """Returns product detailed information based on product ID

    Supported HTTP methods: GET
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(request)
    else:
        ctx = {}

        current_product = get_object_or_404(Product, pk=pk)

        ctx["product name"] = current_product.title
        ctx["price"] = current_product.price
        ctx["availability"] = current_product.inventory_count
        ctx["category"] = current_product.category
        ctx["description"] = current_product.description
        ctx["seller"] = current_product.seller.username

        return JsonResponse(ctx)


@login_required()
def api_retrieve_cart(request):
    """Returns user's cart information including items list, total cost

    Supported HTTP methods: GET
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(request)
    else:
        ctx = {}

        current_cart, created = Cart.objects.get_or_create(user=request.user)

        cart_entries = CartEntry.objects.values(
            "id",
            "product__title",
            "product_count",
            "cost"
        ).filter(
            associated_cart=current_cart
        )

        ctx["overview"] = current_cart.__str__()
        ctx["owner"] = current_cart.user.username
        ctx["items"] = current_cart.item_count
        ctx["total"] = current_cart.total_cost
        ctx["items list"] = list(cart_entries)

        return JsonResponse(ctx)


@login_required()
def api_add_to_cart(request, pk):
    """API view to add a product to cart.

    Supported HTTP methods: GET, POST

    :param request: Current request
    :param pk: Product's ID
    """
    current_product = get_object_or_404(Product, pk=pk)

    ctx = {}

    if request.method == "GET":
        # Render form with CSRF token
        form = CartEntryAddForm()

        ctx["form"] = form
        ctx["product"] = current_product.title
        ctx["available"] = current_product.inventory_count
        ctx["price"] = current_product.price

        return render(request, "marketplace/add-to-cart.html", ctx)
    elif request.method == "POST":
        current_cart, created = Cart.objects.get_or_create(user=request.user)

        form = CartEntryAddForm(request.POST)

        try:
            if form.is_valid():
                # Process data in form.cleaned_data as required
                if current_product.inventory_count < form.cleaned_data["product_count"]:
                    ctx["success"] = False
                    ctx["message"] = "Cannot add more than the current number of available items."
                else:
                    new_cart_entry = form.save(commit=False)

                    # Adding necessary information before adding to database
                    new_cart_entry.associated_cart = current_cart
                    new_cart_entry.product = current_product
                    new_cart_entry.save()

                    ctx["success"] = True
            else:
                ctx["success"] = False
                ctx["message"] = "Invalid form data!"
        except (ValidationError, IntegrityError, ProductNotAvailableException):
            ctx["success"] = False
            ctx["message"] = "Invalid data or cart entry already exists!"

        return JsonResponse(ctx)
    else:
        return HttpResponseNotAllowed(request)


@login_required()
def api_update_cart_entry(request, pk):
    """API view to update a cart entry

    Supported HTTP methods: GET, POST

    :param request: Current request
    :param pk: Cart entry's ID
    """
    current_cart_entry = get_object_or_404(CartEntry, pk=pk)
    current_product = current_cart_entry.product

    ctx = {}

    if request.user != current_cart_entry.associated_cart.user:
        # An outsider should not manipulate other people's carts
        return HttpResponseForbidden(request)
    if request.method == "GET":
        # Render form with CSRF token
        form = CartEntryUpdateForm(instance=current_cart_entry)

        ctx["form"] = form
        ctx["cart_entry_id"] = current_cart_entry.id
        ctx["product"] = current_product.title
        ctx["available"] = current_product.inventory_count
        ctx["price"] = current_product.price

        return render(request, "marketplace/update-cart.html", ctx)
    elif request.method == "POST":
        if request.POST.get("_method") == "delete":
            # A bit of workaround instead of sending DELETE requests
            current_cart_entry.delete()
            return HttpResponse(request, status=204)

        form = CartEntryUpdateForm(request.POST, instance=current_cart_entry)

        try:
            if form.is_valid():
                # Process data in form.cleaned_data as required
                if current_product.inventory_count < form.cleaned_data["product_count"]:
                    ctx["success"] = False
                    ctx["message"] = "Cannot add more than the current number of available items."
                else:
                    form.save()
                    ctx["success"] = True
            else:
                ctx["success"] = False
                ctx["message"] = "Invalid form data!"
        except (ValidationError, ProductNotAvailableException):
            ctx["success"] = False
            ctx["message"] = "Invalid form data!"

        return JsonResponse(ctx)
    else:
        return HttpResponseNotAllowed(request)


@login_required()
def api_checkout_cart_entry(request, pk):
    """API view to checkout a cart entry

    Supported HTTP methods: POST

    :param request: Current request
    :param pk: Cart entry's ID
    """
    if request.method == "POST":
        current_cart_entry = get_object_or_404(CartEntry, pk=pk)

        if request.user != current_cart_entry.associated_cart.user:
            return HttpResponseForbidden(request)
        else:
            ctx = {}

            try:
                CartEntry.checkout_entry(pk=pk)
                ctx["success"] = True
            except ValueError:
                ctx["success"] = False

            return JsonResponse(ctx)
    else:
        return HttpResponseNotAllowed(request)


@login_required()
def api_checkout_cart(request):
    """API view to checkout cart

    Supported HTTP methods: POST

    :param request: Current request
    """
    if request.method == "POST":
        current_cart, created = Cart.objects.get_or_create(user=request.user)

        ctx = {}

        try:
            Cart.checkout_cart(pk=current_cart.id)
            ctx["success"] = True
        except ValueError:
            ctx["success"] = False

        return JsonResponse(ctx)
    else:
        return HttpResponseNotAllowed(request)


@login_required()
def update_inventory(request):
    """API view to update inventory"""
    if request.method == "GET":
        # TODO: render a template with form to modify inventory
        return HttpResponseNotAllowed(request)
    elif request.method == "POST":
        return HttpResponse(request, status=204)
    else:
        return HttpResponseNotAllowed(request)
