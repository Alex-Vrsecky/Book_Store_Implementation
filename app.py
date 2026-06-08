# app.py
from flask import Flask, request, make_response, redirect, session
import os

from server import Database, LoginController, CatalogueController, OrderController
from interface import *
from app_frame import AppFrame

app = Flask(__name__)

# establish a shared secret key on webapp load
# all model classes should access this to decode tokens
SHARED_KEY = os.environ.get("SECRET_KEY", os.urandom(32))
app.secret_key = SHARED_KEY

#Initializes DB and Contoller/View Layer
database = Database() #init DB
login_model = LoginController(database, SHARED_KEY) #init LoginController obj
catalogue_model = CatalogueController(database, SHARED_KEY) #init CatalogueController obj
order_model = OrderController(database)

# ESTABLISH TOKEN STATUS
# Check if admin token, user token or no token
def get_authenticated_user():
    token = request.cookies.get('session_token')
    if token:
        payload = login_model.verify_session_token(token)
        if payload:
            username = payload.get('username')
            role = payload.get('role')

            if role == 'Administrator':
                return AdministratorAccount(username)
            
            return CustomerAccount(username)
    return None

@app.route('/')
def home():
    return redirect('/catalogue') # catalogue is home page

@app.route('/login', methods=['GET', 'POST'])
def login():
    # render form with get
    if request.method == 'GET':
        login_form_html = '''
        <div style="display:flex; flex-direction: column; align-items: center; justify-content:center; text-align: center;">
            <h2>Online Bookstore Portal</h2>
            <form action="/login" method="POST" style="display: inline-block; text-align: left;">
                <div style="margin-bottom: 10px;">
                    Username: <input type="text" name="username" required><br><br>
                </div>
                <div style="margin-bottom: 10px;">
                    Password: <input type="password" name="password" required><br><br>
                </div>
                <div style="margin-bottom: 15px; text-align:center;">
                    <input type="submit" value="Login">
                </div>
            </form>
        </div>
        '''
        return AppFrame.render(login_form_html, user=None)

    # handle form submission with post
    if request.method == 'POST':
        username = request.form.get('username') # retrieves the filled username
        password = request.form.get('password') # retrieves the filled password

        user_data = login_model.validate_credentials(username, password) # validates credentials

        if user_data and "token" in user_data:
            response = make_response(redirect('/dashboard')) # creates redirect reponse
            response.set_cookie('session_token', user_data["token"], httponly=True) #set session cookie
            return response
        
        error_html = '''
            <h2>Login Failed</h2>
            <p> Incorrect username/password.</p>
            <a href="/login">Try Again</a>
        '''

        return AppFrame.render(error_html, user=None) # render failure page

@app.route('/dashboard')
def dashboard(): # dashboard acts as account page for users, portal for admins
    user = get_authenticated_user() # gets user from token
    
    # use appropriate view for admin or customer
    if user:
        #render_dachboard presents differently in admin and user child classes
        return user.render_dashboard()
        
    # missing token catch
    return redirect('/login')
    
@app.route('/catalogue')
def catalogue(): 
    # cat model gets books and passes them to cat view to render on UI
    user = get_authenticated_user()
    search_query = request.args.get('search', "").strip() # search parameter
    author_filter = request.args.get('author', "").strip() # author filter parameter

    result = catalogue_model.browse_and_filter(
        search_query = search_query, 
        author_filter = author_filter
    )
    books = result["data"] if result.get("success") else [] # get filtered list
    return Catalogue.render( # renders catalogue page
        books=books, 
        user=user, 
        current_search=search_query, 
        current_author=author_filter
    )

@app.route('/book/<isbn>') 
def book_detail(isbn):
    user = get_authenticated_user() # current user
    book = catalogue_model.get_book_by_isbn(isbn) # retrieve book specific details
    return Book.render_detail(book, user=user) # renders detailed book page




@app.route('/stock')
def inventory_stock_record():
    user = get_authenticated_user() 

    if not user or not isinstance(user, AdministratorAccount): 
        return redirect('/login')

    inventory_stock_data = catalogue_model.get_inventory_report() # gets all books for stock update page
    return user.render_stock_record(inventory_stock_data) # renders stock update page for admin


@app.route('/catalogue/manage', methods=['GET', 'POST'])
def manage_catalogue(): # Modifying catalogue entries and inventory
    user = get_authenticated_user()
    if not user or not isinstance(user, AdministratorAccount):
        return redirect('/login')
    
    if request.method == 'GET': # If page is requested for viewing, fetch all books from database
        catalogue_books = catalogue_model.get_all_books()
        return user.render_management_page(catalogue_books)
    
    if request.method == 'POST':# If form is submitted (updating stock), extract ISBN from form
        isbn = request.form.get('isbn')
        token= request.cookies.get('session_token') # Retrieves session token

        if 'new_stock' in request.form: # Checks if action is to publish book
            amount = int(request.form.get('new_stock', 0)) # Parse stock quantity to integer
            catalogue_model.add_new_book(token, isbn, "Book Title Placeholder", amount) # Call model to add book


        elif 'operation' in request.form: # Checks if action is updating existing book in catalogue
            amount = int(request.form.get('amount', 0))
            operation = request.form.get('operation')
            catalogue_model.update_catalogue_stock(token, isbn, amount, operation)

        return redirect('/catalogue/manage')
    


## ALL CART OPERATIONS BELOW

@app.route('/cart')
def cart():
    user = get_authenticated_user() 
    if not user or not isinstance(user, CustomerAccount):
        return redirect('/login')
    
    cart_items = order_model.get_cart_items(user.username) # loads users cart
    return ShoppingCart.render(cart_items, user=user) # renders users cart page



@app.route('/cart/add', methods=['POST']) # Process cart addition
def add_to_cart():
    user = get_authenticated_user()
    if not user or not isinstance(user, CustomerAccount):
        return redirect('/login')
    
    isbn = request.form.get("isbn") # gets ISBN from targeted book
    if isbn:
        order_model.add_to_cart(user.username, isbn) # passes to model to add to database
    return redirect("/cart") # sends user to shopping cart page/view


@app.route('/cart/update', methods=['POST']) # Route to handle quantity update to cart items
def update_cart():
    user = get_authenticated_user()
    if not user or not isinstance(user, CustomerAccount):
        return redirect('/login')
    
    for key, value in request.form.items():
        if key.startswith("quantity_"): # handles each quantity input
            isbn = key.replace("quantity_", "") # extracts books individual ISBN
            order_model.update_cart_item(user.username,isbn,value) # updates cart row
    
    return redirect('/cart') # refreshes cart page


@app.route('/cart/clear', methods=['POST']) # Route to empty cart
def clear_cart():
    user = get_authenticated_user()
    if not user or not isinstance(user, CustomerAccount):
        return redirect('/login')
        
    order_model.clear_cart(user.username) # database removes all cart items for user
    return redirect('/cart') # refresh cart page



# Payment/Invoice Operations

@app.route('/invoice', methods=['GET']) # Route to display invoice summary
def invoice():
    user = get_authenticated_user()
    if not user or not isinstance(user, CustomerAccount):
        return redirect('/login')
    
    invoice_data = order_model.get_invoice_details(user.username) # fetches invoice details for user

    if not invoice_data:
        return redirect('/cart')

    return Invoice.render(invoice_data, user=user) # renders invoice page with details



@app.route('/payment', methods=['POST']) # Route to process shipping info
def payment():
    user = get_authenticated_user()
    if not user or not isinstance(user, CustomerAccount):
        return redirect('/login')
    
    session['shipping_info'] = { # Saves shipping details in secure session
            "name": request.form.get("name"),
            "address": request.form.get("address"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone")
        }

    invoice_data = order_model.get_invoice_details(user.username) # fetches invoice details for user

    return Payment.render(invoice_data, session['shipping_info'], user=user) # renders payment page with invoice and shipping details




@app.route('/pay', methods=['POST']) # Final Route to process transaction
def pay():
    user = get_authenticated_user()
    if not user or not isinstance(user, CustomerAccount):
        return redirect('/login')

    
    shipping_info = session.get('shipping_info') # Retrieve stored shipping info
    if not shipping_info:
        return redirect('/cart') 
    
    invoice_data = order_model.get_invoice_details(user.username) # Get invoice totals
    if not invoice_data or "total" not in invoice_data: # Validate totals exist
        return redirect('/cart')
    
    card_details = { # Pack credit card details
        "card_name": request.form.get("card_name"),
        "card_number": request.form.get("card_number"),
        "expiry": request.form.get("expiry"),
        "cvv": request.form.get("cvv"),
    }

    success, message = order_model.process_customer_order( # Process order via model
        user.username,
        card_details,
        shipping_info["address"],
        invoice_data["total"]
    )

    user_email = shipping_info.get('email') if shipping_info else None # Store email for receipt

    session.pop('shipping_info', None) # Clear shipping info after processing

    return Receipt.render(success, message,user=user, email= user_email) # simple success page after payment

# Shipping Routes

@app.route('/shipping') # Route for admin shipping view
def shippingportal():
    user = get_authenticated_user()
    if not isinstance(user, AdministratorAccount):
        return redirect('/login')
    
    all_orders = order_model.get_all_orders() # Get all system orders
    return Shipment.render_management_page(all_orders, user=user)


@app.route('/shipment/update', methods=['POST']) # Route to change order status
def update_shipment():
    user = get_authenticated_user()
    if not isinstance(user, AdministratorAccount):
        return redirect('/login')
    
    order_num = request.form.get("order_num") # Get order number
    new_status = request.form.get("new_status") # Get new status

    if order_num and new_status:
        order_model.update_order_status(order_num, new_status) # Update via mordel

    return redirect('/shipping')
    
@app.route('/order') # Route to View order history (for customers)
def order_history():
    user = get_authenticated_user()
    if not isinstance(user, CustomerAccount): 
        return redirect('/login')
    
    orders = order_model.get_orders_by_username(user.username) # Get order history for user
    return Order.render_history(orders, user=user)

@app.route('/order/<order_num>') # Route to View specific order (order details)
def order_details(order_num):
    user = get_authenticated_user()

    if not user:
        return redirect('/login')
    
    full_order_id = f"Order#{order_num}" # Format id to match database
    order_data = order_model.get_order_by_num(full_order_id) # Get order data

    
    if not order_data:  # If order does not exist
        return f"Order {full_order_id} not found."
    
    items = order_model.get_order_items(full_order_id) # Get line items
    return Order.render_details(full_order_id, items, user=user) # Renders page


@app.route('/logout') # Logout Route
def logout():
    response = make_response(redirect('/')) 
    # expire token by setting its expiry time to 0
    response.set_cookie('session_token', '', expires=0) # Delete cookie by expiring it
    return response

if __name__ == '__main__':
    app.run(port=5000, debug=True)