# my-marketplace [![Build Status](https://travis-ci.com/trungams/my-marketplace.svg?token=ZLjfN4mmyQ4ZCqssRxs2&branch=master)](https://travis-ci.com/trungams/my-marketplace)

My API design of an online marketplace. For Shopify application

## The framework

Since web API is not my true forte, I chose Django, a framework that I'm more used to, which incidently simplifies quite a few steps in the development process. I could choose to go RESTful but I also took advantage of the Model View Template pattern of Django. So in addition to return pure data, some of my endpoints may give Html files as responses.

## Installation and running the site locally

## My design

## The API

I decided to do some extra work because it makes the logic of my API clearer. In summary, these endpoints are supported:

- / or /marketplace
  - Endpoint name: Index
  - Supported HTTP methods: All
  - What it does: Returns the index page
- /login
  - Endpoint name: Login
  - Supported HTTP methods: GET, POST
  - Restrictions: POST request requires a CSRF token
  - What it does:
    - GET: Returns a login form
    - POST: Sends a user's credentials to server for authentication. If valid, the user will be logged in
- /logout
  - Endpoint name: Logout
  - Supported HTTP methods: GET
  - What it does: Signs out a logged in user
- /register
  - Endpoint name: Register
  - Supported HTTP methods: GET, POST
  - Restrictions: POST request requires a CSRF token
  - What it does:
    - GET: Returns a registration form
    - POST: Sends information to server to create a new account. If form data are valid, a new account will be created and can be used to login
- /marketplace/api/products/view
  - Endpoint name: View products
  - Supported HTTP methods: GET
  - What it does:
    - GET: Retrieves information about products on marketplace. Some GET parameters are supported to filter search results. Supported parameters are:
      - product (string): search based on name of products.
      - category (string): search based on category of products.
      - availability (true/false): search based on products' availability. If the value is true, only products with inventory > 0 will be shown.
- /marketplace/api/products/<product_id>/view
  - Endpoint name: View specific product
  - Supported HTTP methods: GET
  - What it does:
    - GET: Retrieves information about a product with ID <product_id>. If such ID does not exist in the store, a 404 error code will be returned    
- /marketplace/api/products/<product_id>/checkout
  - Endpoint name: Purchase a product
  - Supported HTTP methods: POST
  - What it does:
    - POST: Decrease the inventory count of a product with ID <product_id> by 1, similar to a "purchase" in real life and returns the result of the purchase (success or not)
- /marketplace/api/products/<product_id>/add-to-cart
  - Endpoint name: Add product to cart
  - Supported HTTP methods: GET, POST
  - Restrictions: User must be logged in. POST request requires a CSRF token
  - What it does:
    - GET: Returns a form to choose the number of items to add to cart
    - POST: Adds a number of items of a product to user's cart if form data are valid and returns the status of the action (success/fail)
- /marketplace/api/cart/view
  - Endpoint name: View cart
  - Supported HTTP methods: GET
  - Restrictions: User must be logged in
  - What it does:
    - GET: Returns information about a user's cart including all cart entries
- /marketplace/api/cart/<cart_entry>/update
  - Endpoint name: Update cart entry
  - Supported HTTP methods: GET, POST
  - Restrictions: User must be logged in. POST request requires a CSRF token
  - What it does:
    - GET: Returns a form to choose modify the number of items in a cart entry with ID <carty_entry>, if the ID is valid.
    - POST: Updates the corresponding cart entry if form data are valid
- /marketplace/api/cart/<cart_entry>/checkout
  - Endpoint name: Checkout cart entry
  - Supported HTTP methods: POST
  - Restrictions: User must be logged in. POST request requires a CSRF token
  - What it does:
    - POST: Checks out a cart entry and update inventory of the product
- /marketplace/api/cart/checkout
  - Endpoint name: Checkout cart
  - Supported HTTP methods: POST
  - Restrictions: User must be logged in. POST request requires a CSRF token
  - What it does:
    - POST: Checks out a cart by iterating through all cart entries and performs a checkout on every entry. Throws a warning on unsuccessful entry checkout

## What I did

## A few things I have learned over the past week
