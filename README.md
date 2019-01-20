# my-marketplace [![Build Status](https://travis-ci.com/trungams/my-marketplace.svg?token=ZLjfN4mmyQ4ZCqssRxs2&branch=master)](https://travis-ci.com/trungams/my-marketplace)

My API design of an online marketplace. For Shopify application.
- Name: Trung Vuong Thien
- Email: trung.vuongthien@mail.mcgill.ca


## Table of contents

- [My submission](#my-submission)
- [The framework](#the-framework)
- [Installation and running the site locally](#installation-and-running-the-site-locally)
- [My design](#my-design)
- [The API](#the-api)
  - [Easier-to-test endpoints](#easier-to-test-endpoints)
  - [Endpoints that may require login or CSRF token](#endpoints-that-may-require-login-or-csrf-token)
- [What I did](#what-i-did)
- [Some notes](#some-notes)


## My submission

Even though I'm submitting via a zip file, you can view my entire work history on Github, including issues tracking and build status. Here is the link to the repo: https://github.com/trungams/my-marketplace. It is a private repo, so if you want to be able to access it, please send me an email at trung.vuongthien@mail.mcgill.ca with your Github username, I will add you as a collaborator.


## The framework

Since web API is not my true forte, I chose Django, a Python web framework that I'm more used to, which incidently simplifies quite a few steps in the development process. I could choose to go RESTful but I also took advantage of the Model View Template pattern of Django. So in addition to return pure data, some of my endpoints may give Html files as responses.


## Installation and running the site locally

The computer I'm using to develop this API is running Ubuntu 18.04. I'm using Pipenv to manage packages and virtual environment. To install pipenv, run the following commands:

```bash
# To install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3 get-pip.py

# To install pipenv
sudo pip install pipenv
```

Please follow these steps in order to get the project up and running on your localhost:

```bash
# To install dependencies
pipenv install

# Activate pipenv shell, your command prompt will then look like '(my-marketplace) <original prompt>'
pipenv shell

# To set up and populate the database with some dummy entries
python manage.py makemigrations
python manage.py migrate
python initdb.py

# To run the server
python manage.py runserver
```

Go to http://localhost:8000/, and you will see the index page, or send HTTP requests to the URLs mentioned [below](#the-api)


## My design

My marketplace is built around 4 main models, and has 12 endpoints in total. I will discuss the model design and some basic logic under the hood in this section.

### Models

- Product
  - The most important model of this marketplace. Each product in database represents one type of goods sold on my marketplace in real life. Each product entry in the database includes product id, title, price, inventory_count, category, description, and the seller, who is also a user of the website. A product can be checked out.
- User
  - This model represents a user of the website, who can log in, log out, query a product and add a product to their personal shopping cart, and can check out a shopping cart.
- Cart
  - Represents a shopping cart. A cart can only belong to one user and vice versa. A cart will store information of the number of items in cart, and the total cost. A cart can be checked out, decreasing the inventory count of related products if the transaction is successful.
- CartEntry
  - Represents a connection between a product and a specific cart. A cart can have multiple entries, which stand for one type of product on marketplace. For example, there are a dozen eggs and 2 tomatoes in my shopping cart. The eggs and tomatoes make 2 entries in the cart, with the item count of 12 and 2, respectively. A cart entry can be checked out separately.


## The API

I decided to do some extra work and add carts and user authentication because it makes the logic of my API clearer. In summary, these endpoints are supported:

### Easier-to-test endpoints
- [/ or /marketplace](#-or-marketplace)
- [/marketplace/api/products/view](#marketplaceapiproductsview)
- [/marketplace/api/products/<product_id>/view](#marketplaceapiproductsproduct_idview)
- [/marketplace/api/products/<product_id>/checkout](#marketplaceapiproductsproduct_idcheckout)

### Endpoints that may require login or CSRF token

- [/login](#login)
- [/logout](#logout)
- [/register](#register)
- [/marketplace/api/products/<product_id>/add-to-cart](#marketplaceapiproductsproduct_idadd-to-cart)
- [/marketplace/api/cart/view](#marketplaceapicartview)
- [/marketplace/api/cart/<cart_entry>/update](#marketplaceapicartcart_entryupdate)
- [/marketplace/api/cart/<cart_entry>/checkout](#marketplaceapicartcart_entrycheckout)
- [/marketplace/api/cart/checkout](#marketplaceapicartcheckout)

#### / or /marketplace
  - Endpoint name: Index
  - Supported HTTP methods: All
  - What it does: Returns the index page
#### /login
  - Endpoint name: Login
  - Supported HTTP methods: GET, POST
  - Restrictions: POST request requires a CSRF token
  - What it does:
    - GET: Returns a login form
    - POST: Sends a user's credentials to server for authentication. If valid, the user will be logged in
#### /logout
  - Endpoint name: Logout
  - Supported HTTP methods: GET
  - What it does: Signs out a logged in user
#### /register
  - Endpoint name: Register
  - Supported HTTP methods: GET, POST
  - Restrictions: POST request requires a CSRF token
  - What it does:
    - GET: Returns a registration form
    - POST: Sends information to server to create a new account. If form data are valid, a new account will be created and can be used to login
#### /marketplace/api/products/view
  - Endpoint name: View products
  - Supported HTTP methods: GET
  - What it does:
    - GET: Retrieves information about products on marketplace. Some GET parameters are supported to filter search results. Supported parameters are:
      - product (string): search based on name of products.
      - category (string): search based on category of products.
      - availability (true/false): search based on products' availability. If the value is true, only products with inventory > 0 will be shown.
#### /marketplace/api/products/<product_id>/view
  - Endpoint name: View specific product
  - Supported HTTP methods: GET
  - What it does:
    - GET: Retrieves information about a product with ID <product_id>. If such ID does not exist in the store, a 404 error code will be returned    
#### /marketplace/api/products/<product_id>/checkout
  - Endpoint name: Purchase a product
  - Supported HTTP methods: POST
  - What it does:
    - POST: Decrease the inventory count of a product with ID <product_id> by 1, similar to a "purchase" in real life and returns the result of the purchase (success or not)
#### /marketplace/api/products/<product_id>/add-to-cart
  - Endpoint name: Add product to cart
  - Supported HTTP methods: GET, POST
  - Restrictions: User must be logged in. POST request requires a CSRF token
  - What it does:
    - GET: Returns a form to choose the number of items to add to cart
    - POST: Adds a number of items of a product to user's cart if form data are valid and returns the status of the action (success/fail)
#### /marketplace/api/cart/view
  - Endpoint name: View cart
  - Supported HTTP methods: GET
  - Restrictions: User must be logged in
  - What it does:
    - GET: Returns information about a user's cart including all cart entries
#### /marketplace/api/cart/<cart_entry>/update
  - Endpoint name: Update cart entry
  - Supported HTTP methods: GET, POST
  - Restrictions: User must be logged in. POST request requires a CSRF token
  - What it does:
    - GET: Returns a form to choose modify the number of items in a cart entry with ID <carty_entry>, if the ID is valid.
    - POST: Updates the corresponding cart entry if form data are valid
#### /marketplace/api/cart/<cart_entry>/checkout
  - Endpoint name: Checkout cart entry
  - Supported HTTP methods: POST
  - Restrictions: User must be logged in. POST request requires a CSRF token
  - What it does:
    - POST: Checks out a cart entry and update inventory of the product
#### /marketplace/api/cart/checkout
  - Endpoint name: Checkout cart
  - Supported HTTP methods: POST
  - Restrictions: User must be logged in. POST request requires a CSRF token
  - What it does:
    - POST: Checks out a cart by iterating through all cart entries and performs a checkout on every entry. Throws a warning on unsuccessful entry checkout


## What I did

- With the help of Django, I can set up a database quite quickly with all the defined fields and constraints. I then added some methods for each model class to simulate transaction and querying data.
- I defined views (similar to controllers in an MVC pattern) as the backend logic of the website, which is responsible for authenticating users, evaluating requests and manipulating the database.
- I tests for each model class and view function.
- I tried to write comments (documentation style) for each class and function.
- I added Continuous Integration to automatically run tests whenever I push to Github.


## Some notes

- Brainstorming, designing, implementing, testing is tiring.
- Fixing bugs is tiring.
- Some concurrency problem I learned in my Operating Systems class turned out to be very helpful.
- I almost caused a huge bug because I did not authenticate users carefully.
- I'm glad that I'm able to finish this. Thank you for the challenge!
