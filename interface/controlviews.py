# controlviews.py
from app_frame import AppFrame

class Account:
    def __init__(self, username):
        self.username = username

    def render_dashboard(self):
        raise NotImplementedError("Subclasses must render their own views.")


class CustomerAccount(Account):
    # render a user account dashboard at /dashboard
    def render_dashboard(self):
        inner_html = f'''
            <h2>Your Account</h2>
            <p>Welcome back, <strong>{self.username}</strong></p>
            <hr>
            <ul style="display:flex; list-style: none; padding: 0; gap: 10px; justify-content: space-between;">
                <li style="border: 1px solid #ccc; background-color: #333; padding: 10px; flex: 1; text-align: center;"><a href="/catalogue" style="color:#fff; text-decoration: none;">Browse Book Catalogue</a></li>
                <li style="border: 1px solid #ccc; background-color: #333; padding: 10px; flex: 1; text-align: center;"><a href="/cart" style="color:#fff; text-decoration: none;">View Shopping Cart</a></li>
                <li style="border: 1px solid #ccc; background-color: #333; padding: 10px; flex: 1; text-align: center;"><a href="/order" style="color:#fff; text-decoration: none;">View Order History</a></li>
                <li style="border: 1px solid #ccc; background-color: #333; padding: 10px; flex: 1; text-align: center;"><a href="/logout" style="color:#fff; text-decoration: none;">Logout</a></li>
            </ul>
        '''
        return AppFrame.render(inner_html, user=self)


class AdministratorAccount(Account):
    # render an admin dashboard at /dashboard
    def render_dashboard(self):
        inner_html = f'''
            <h2>Admin Portal</h2>
            <p>Staff ID Identity: <strong>{self.username}</strong></p>
            <p>Security Clearance: Multi-Factor Confirmed</p>
            <hr>
            <ul style="display:flex; list-style: none; padding: 0; gap: 10px; justify-content: space-between;">
                <li style="border: 1px solid #ccc; background-color: #333; padding: 10px; flex: 1; text-align: center;"><a href="/stock" style="color:#fff; text-decoration: none;">Inventory Stock Levels</a></li>
                <li style="border: 1px solid #ccc; background-color: #333; padding: 10px; flex: 1; text-align: center;"><a href="/catalogue/manage" style="color:#fff; text-decoration: none;">Manage Book Catalogue</a></li>
                <li style="border: 1px solid #ccc; background-color: #333; padding: 10px; flex: 1; text-align: center;"><a href="/shipping" style="color:#fff; text-decoration: none;">Manage Orders</a></li>
                <li style="border: 1px solid #ccc; background-color: #333; padding: 10px; flex: 1; text-align: center;"><a href="/logout" style="color:#fff; text-decoration: none;">Logout</a></li>
            </ul>
        '''
        return AppFrame.render(inner_html, user=self)
    # Builds a table showing inventory status for admin
    def render_stock_record(self, inventory_items):
        rows = ""
        for b in inventory_items:
            # Styling based on publication status
            if b.get("is_published"):
                status = '<span style= "color: green;">Yes</span>'
            else:
                status = '<span style="color: red;">No</span>'

            rows += f'''
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;">{b["isbn"]}</td>
                <td><strong>{b["title"]}</strong><br><small>{b["author"]}</small></td>
                <td style="color: #0288d1;">{b["stock"]} units</td>
                <td>{status}</td>
            </tr>
            '''
        inner_html = f'''
            <h2>Inventory Stock Levels</h2>
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <tr style="background-color: #f5f5f5;">
                    <th style="padding: 10px;">ISBN Reference</th>
                    <th>Book details</th>
                    <th>Unpublished Stock</th>
                    <th>Book Published In Catalogue</th>
                </tr>
                {rows}
            </table>

            <div style="text-align: center; margin-top:20px;">
                <a href="/dashboard" style="display:inline-block; padding: 10px 20px; text-decoration: none; background: #333; color:#fff; border:none; cursor:pointer">Back to Admin Dashboard</a>
            </div>
        '''
        return AppFrame.render(inner_html, user=self)
    # Builds a form-based interface for admins to add/remove stocks for existing books and add new ones
    def render_management_page(self, catalogue_books):
        rows = ""
        for b in catalogue_books:
            rows += f'''
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;">{b["isbn"]}</td>
                <td><strong>{b["title"]}</strong>
                <td style="color: #0288d1;">{b["stock"]} units on shelves</td>
                <td>
                    <form action="/catalogue/manage" method="POST" style="display:flex; gap:5px; align-items:center;">
                        <input type="hidden" name="isbn" value="{b["isbn"]}">
                        <select name="operation">
                            <option value="add">Add</option>
                            <option value="remove">Remove</option>
                        </select>
                        <input type="number" name="amount" min="0" style="width:70px; padding:4px;" required>
                        <button type="submit" style="padding:4px 8px;">Apply</button>
                    </form>
                </td>
            </tr>
            '''
        inner_html = f'''
            <h2>Catalogue Management</h2>
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <tr style="background-color: #f5f5f5;">
                    <th style="padding: 10px;">ISBN Reference</th>
                    <th>Book details</th>
                    <th>Stock Level</th>
                    <th>Adjust stock</th>
                </tr>
                {rows}
            </table>
                

            <div style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 4px; display:flex; flex-direction: column; align-items:center; text-align:center;">
                <h3>Add New Book to Catalogue</h3>
                <form action="/catalogue/manage" method="POST" style="display:flex; gap:10px; max-width:450px;">
                    <input type="text" name="isbn" placeholder="978-XXXXXXXXXX" style="padding:6px; flex:1;" required>
                    <input type="number" name="new_stock" placeholder="Initial shelf quantity" min="1" style="width:140px; padding:6px;" required>
                    <input type="submit" value="Publish" style="background: #2e7d32; color:white; border:none; padding:6px 12px; cursor:pointer; border-radius:4px;">
                </form>
            </div>

            <div style="text-align: center; margin-top:20px;">
                <a href="/dashboard" style="display:inline-block; padding: 10px 20px; text-decoration: none; background: #333; color:#fff; border:none; cursor:pointer">Back to Admin Dashboard</a>
            </div>
        '''
        return AppFrame.render(inner_html, user=self)
    
class Catalogue:
    @staticmethod
    # render the catalogue homepage
    def render(books, user=None, current_search="", current_author=""):
        # Individual book HTML !!! MUST MOVE TO BOOK CLASS !!!
        books_html = "".join([Book.render_card(b, user) for b in books])

        # no books matched search
        if not books_html:
            books_html = "<p style='grid-column: span 3; color: #666;'>No books match your criteria.</p>"

        
        # overall search interface
        inner_html = f'''
            <h2>Book Catalogue</h2>
            
            <form action="/catalogue" method="GET" style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 4px;">
                <input type="text" name="search" placeholder="Search by title..." value="{current_search}" style="padding: 8px; width: 250px;">
                <input type="text" name="author" placeholder="Filter by author..." value="{current_author}" style="padding: 8px; width: 200px;">
                <input type="submit" value="Apply Filters" style="padding: 8px 15px; background: #333; color: white; border: none; cursor: pointer;">
                <a href="/catalogue" style="margin-left: 10px; font-size: 14px; color: #666;">Clear Filters</a>
            </form>
            
            <hr>
            
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                {books_html}
            </div>
        '''
        return AppFrame.render(inner_html, user=user)
    
class Book:
    @staticmethod
    # Renders a summary card of specific book
    def render_card(book, user=None):
        stock_available = book.get("stock", 0) > 0
        stock_status = "Available" if stock_available else "Out of stock"
        stock_color = "green" if stock_available else "red"

        return (
            f'<div style="border:1px solid #ccc; padding:10px; margin:5px; border-radius:4px;">'
            f'<a href="/book/{book["isbn"]}" style="text-decoration:none; color:#222;">'
            f'<h3>{book["title"]}</h3>'
            f'</a>'
            f'<p><strong>Author:</strong> {book.get("author", "Unknown")}</p>'
            f'<p>Price: ${book["price"]}</p>' 
            f'<p><strong>Stock:</strong> <span style="color:{stock_color};">{stock_status}</span></p>'
            f'</div>'
        )
    
    @staticmethod
    # Renders expanded view for single book
    def render_detail(book, user=None):
        if not book:
            inner_html = '''
                <h2>Book Not Found</h2>
                <p>Sorry, the book you are looking for does not exist.</p>
                <a href="/catalogue">Back to Catalogue</a>
            '''
            return AppFrame.render(inner_html, user=user)
        # Displays Add to Cart button if book is in store
        stock_status = "In stock" if book["stock"] > 0 else "Out of stock"
        stock_color = "green" if book["stock"] > 0 else "red"
        add_button = ""
        if book["stock"] > 0:
            add_button = (
                f'<form action="/cart/add" method="POST" style="display:inline-block;">'
                f'  <input type="hidden" name="isbn" value="{book["isbn"]}">'
                f'  <button type="submit" style="padding:8px 12px; margin-top:10px; background: #333; color:#fff; border:none; cursor:pointer; border-radius:4px;">Add to Cart</button>'
                f'</form>'
            )
        
        inner_html = f'''
            <h2>{book["title"]}</h2>
            <p><strong>Author:</strong> {book.get("author", "Unknown")}</p>
            <p><strong>ISBN:</strong> {book["isbn"]}</p>
            <p><strong>Price:</strong> ${book["price"]}</p>
            <p><strong>Stock status:</strong> <span style="color:{stock_color};">{stock_status}</span></p>
            <div style="text-align:center; margin-top:12px;">
                {add_button}
                <div style="margin-top:12px;">
                    <a href="/catalogue" style="display:inline-block; padding:10px 16px; background:#695757; color:#fff; text-decoration:none;">Back to Catalogue</a>
                </div>
            </div>
        '''
        return AppFrame.render(inner_html, user=user)

class ShoppingCart:
    @staticmethod 
    # Renders cart contents with update/delete capabilities
    def render(cart_items, user=None):
        if not cart_items:
            inner_html = '''
                <h2>Shopping Cart</h2>
                <p> You cart is empty.</p>
                <div style="display:flex; justify-content:center; gap: 20px;">
                    <a href="/catalogue" style="padding: 10px 15px; background:#851818; color:#fff; border:none; text-decoration:none;">
                        Continue Shopping
                    </a>
                </div>
            '''
            return AppFrame.render(inner_html, user= user)
        
        # Builds cart rows dynamically
        rows = "".join([
            f'''
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item["title"]}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item["author"]}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align:right;">${item["price"]:.2f}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align:right;">
                    <input type="number" name="quantity_{item["isbn"]}" value="{item["quantity"]}" min="0" max="10" style="width:50px; text-align:right;">
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align:right;">${item["price"] * item["quantity"]:.2f}</td>
            </tr>
            '''
            for item in cart_items
        ])
        total = sum(item["price"] * item["quantity"] for item in cart_items)

        inner_html = f'''
            <h2>Shopping Cart</h2>
            <form action="/cart/update" method="POST">
                <table style = "width:100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr>
                            <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ccc;">Title</th>
                            <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ccc;">Author</th>
                            <th style="text-align: right; padding: 8px; border-bottom: 1px solid #ccc;">Price</th>
                            <th style="text-align: right; padding: 8px; border-bottom: 1px solid #ccc;">Qty</th>
                            <th style="text-align: right; padding: 8px; border-bottom: 1px solid #ccc;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>

                <p style="text-align:right; font-weight:bold;">Total: ${total:.2f}</p>

                <div style="display:flex; justify-content:center; gap: 10px; margin-bottom:10px;">
                    <button type="submit" style="padding: 10px 15px; background:#333; color:#fff; border:none; cursor:pointer;">
                        Update Cart
                    </button>
                </div>
            </form>

            <div style="display:flex; justify-content: center; margin-bottom: 10px; gap:10px;">
                <form action="/cart/clear" method="POST" style="margin:0;">
                    <button type="submit" style="padding: 10px 15px; background:#c00; color:#fff; border:none; cursor:pointer;">
                        Clear Cart
                    </button>
                </form>
            </div>

            <div style="display:flex; justify-content:center; gap: 20px;">
                <a href="/catalogue" style="padding: 10px 15px; background:#851818; color:#fff; border:none; text-decoration:none;">
                    Continue Shopping
                </a>
                <a href="/invoice" style="padding: 10px 15px; background:#2e7d32; color:#fff; text-decoration:none;">
                    Continue to Invoice
                </a>
            </div>
        '''
        return AppFrame.render(inner_html, user=user)
    

class Invoice:
    @staticmethod
    # Renders the final review before payment (shows shipping form)
    def render(invoice_data, user=None):
        rows = "".join([
            f'''
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item["title"]}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item["quantity"]}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align:right;">${item["price"] * item["quantity"]:.2f}</td>
            </tr>
            '''
            for item in invoice_data["items"]
        ])

        inner_html = f'''
            <h2>Final Order Details</h2>
            <table style = "width:100%; border-collapse: collapse; margin-bottom: 20px;">
                <thead>
                    <tr style="background: #f4f4f4;">
                        <th style="text-align: left; padding: 8px;">Item</th>
                        <th style="text-align: left; padding: 8px;">Qty</th>
                        <th style="text-align: right; padding: 8px;">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            <p style="font-weight:bold; text-align:right;">Total: ${invoice_data["total"]:.2f}</p>
            <hr>
            <h3>Shipping Details</h3>
            <form action="/payment" method="POST">
                Full Name:<input type="text" name="name" style="padding:8px;" required pattern="[A-Za-z ]+" placeholder="e.g. Alex Chen" title="Alphabetical Characters Only"><br>
                Street Address:<input type="text" name="address" style="padding:8px;" required title="Must fill out" placeholder="e.g. 5 Monster Street"><br>
                Email:<input type="email" name="email" style="padding:8px;" placeholder="e.g. alex901@gmail.com" required><br>
                Phone:<input type="text" name="phone" style="padding:8px;" required pattern="[0-9]{{10}}" placeholder="No Spaces" title="Must be 10 digits" maxlength="10"><br>
                <button type="submit" style="padding: 10px 20px; background: #2e7d32; color:#fff; border:none; cursor:pointer; margin-top: 10px;">Proceed to Checkout</button>
            </form>
        '''
        return AppFrame.render(inner_html, user=user)
    
class Payment:
    @staticmethod 
    # Renders final checkout interface with input for payment credentials
    def render(invoice_data, shipping_info, user=None):
        rows= "".join([
            f'''
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item["isbn"]}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item["title"]}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item["author"]}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align:right;">${item["price"]:.2f}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align:center;">{item["quantity"]}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align:right;">${item["price"] * item["quantity"]:.2f}</td>
            </tr>
            '''
            for item in invoice_data["items"]
        ])

        inner_html = f'''
            <h2>Invoice</h2>
            <div style="background:#f9f9f9; padding:15px; border-radius:4px; margin-bottom:15px;">
                <h3>Shipping to:</h3>
                <p><strong>Full Name: </strong>{shipping_info['name']}<br>
                <strong>Delivery Address: </strong>{shipping_info['address']}<br>
                <strong>Email Address: </strong>{shipping_info['email']}<br>
                <strong>Phone Number: </strong>{shipping_info['phone']}</p>
            </div>

            <h3>Order Details:</h3>
            <table style="width:100%; border-collapse: collapse; margin-bottom: 20px;">
                <thead>
                    <tr style="background: #f4f4f4;">
                        <th style="text-align: left; padding: 8px;">ISBN</th>
                        <th style="text-align: left; padding: 8px;">Item</th>
                        <th style="text-align: left; padding: 8px;">Author</th>
                        <th style="text-align: right; padding: 8px;">Price</th>
                        <th style="text-align: center; padding: 8px;">Qty</th>
                        <th style="text-align: right; padding: 8px;">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>

            <h3 style="text-align:right;">Order Total: ${invoice_data["total"]:.2f}</h3>

            <form action="/pay" method="POST">
                <h3>Enter Payment Details</h3>
                Name on Card:<input type="text" name="card_name" style="padding:8px;" required pattern="[A-Za-z ]+" title="Alphabetical Characters Only"><br>
                Card Number:<input type="text" name="card_number" style="padding:8px;" required pattern="^[0-9]+$" placeholder="No Spaces" title="Must be all numbers"><br>
                Expiry Date:<input type="text" name="expiry" style="padding:8px;" required placeholder="MM/YY" maxlength="5"><br>
                CVV:<input type="text" name="cvv" style="padding:8px;" required pattern="[0-9]{{3}}" placeholder="XXX" title="Must be 3 digits"><br>
                <button type="submit" style="padding: 10px 20px; background: #2e7d32; color:#fff; border:none; cursor:pointer; margin-top: 10px;">Place Order & Pay Now</button>
            </form>
        '''
        return AppFrame.render(inner_html, user=user)


class Receipt:
    @staticmethod
    # Renders a success/failure message after payment is received
    def render(success, message, user=None, email=None):
        color = "green" if success else "red"
        title = "Payment successful" if success else "Payment failed"
        email_note = f"<p>A receipt has been sent to {email}.</p>" if (success and email) else ""

        inner_html = f'''
            <h2 style="color:{color};">{title}</h2>
            <div style="padding:20px; border-radius:4px;">
                <p>{message}</p>
                {email_note}
                <div style="margin-top:12px; text-align:center;">
                    <a href="/catalogue" style="display:inline-block; padding:10px 16px; background:#695757; color:#fff; text-decoration:none;">Back to Catalogue</a>
                </div>
            </div>
        '''
        return AppFrame.render(inner_html, user=user)
    
class Shipment:
    @staticmethod
    # Renders the admin table to track and update order delivery statuses
    def render_management_page(orders, user=None):
        rows = ""

        status_colors = {
            "Delivered": "background-color: #e8f5e9;",
            "In-Transit": "background-color: #fff3e0;"
        }

        for o in orders:

            row_style = status_colors.get(o["order_status"], "")
            rows += f'''
            <tr style="border-bottom: 1px solid #ddd; {row_style}">
                <td style="padding: 10px;"><a href="/order/{o["order_num"].split('#')[1]}">{o["order_num"]}</a></td>
                <td style="padding: 10px;">{o["username"]}</td>
                <td style="padding: 10px;">{o["delivery_address"]}</td>
                <td style="padding: 10px;">{o["date_of_order_placed"]}</td>
                <td style="padding: 10px;">{o["courier_name"]}</td>
                <td style="padding: 10px;">{o["delivery_person_name"]}</td>
                <td style="padding: 10px;">{o["delivery_person_phone"]}</td>
                <td>
                    <form action="/shipment/update" method="POST" style="display: flex; gap: 5px;">
                        <input type="hidden" name="order_num" value="{o["order_num"]}">
                        <select name="new_status" style="padding: 5px;">
                            <option value="Processed" {"selected" if o["order_status"] == "Processed" else ""}>Processed</option>
                            <option value="Shipped" {"selected" if o["order_status"] == "Shipped" else ""}>Shipped</option>
                            <option value="In-Transit" {"selected" if o["order_status"] == "In-Transit" else ""}>In-Transit</option>
                            <option value="Delivered" {"selected" if o["order_status"] == "Delivered" else ""}>Delivered</option>
                        </select>
                        <button type="submit" style="padding: 5px 10px; cursor: pointer;">Update</button>
                    </form>
                </td>
            </tr>
            '''

        inner_html = f'''
            <h2>Shipment Management</h2>
            <table style="width: 100%; border-collapse: collapse; text-align:left;">
                <tr style="background-color: #f5f5f5;">
                    <th style="padding: 10px;">Order #</th>
                    <th style="padding: 10px;">Customer</th>
                    <th style="padding: 10px;">Delivery Address</th>
                    <th style="padding: 10px;">Date Of Order Placed</th>
                    <th style="padding: 10px;">Courier</th>
                    <th style="padding: 10px;">Delivery Person</th>
                    <th style="padding: 10px;">Delivery Phone Number</th>
                    <th style="padding: 10px;">Order Status</th>
                </tr>
                {rows}
            </table>

            <div style="text-align: center; margin-top:20px;">
                <a href="/dashboard" style="display:inline-block; padding: 10px 20px; text-decoration: none; background: #333; color:#fff; border:none; cursor:pointer">Back to Admin Dashboard</a>
            </div>
        '''
        return AppFrame.render(inner_html, user=user)
    
class Order:
    @staticmethod
    # Renders list of past orders for logged in user
    def render_history(orders, user=None):
        rows = ""
        for o in orders:
            full_id = o['order_num']
            numeric_id = full_id.split('#')[1]
            rows += f'''
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;"><a href="/order/{numeric_id}">{full_id}</a></td>
                <td style="padding: 10px;">{o['date_of_order_placed']}</td>
                <td style="padding: 10px;">{o['order_status']}</td>
            </tr>
            '''
        inner_html = f'''
            <h2>Your Order History</h2>
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <tr style="background-color: #f5f5f5;">
                    <th style="padding: 10px;">Order #</th>
                    <th style="padding: 10px;">Date of Order Placed</th>
                    <th style="padding: 10px;">Order Status</th>
                </tr>
                {rows}
            </table>
            <div style="text-align: center; margin-top:20px;">
                <a href="/dashboard" style="display:inline-block; padding: 10px 20px; text-decoration: none; background: #333; color:#fff; border:none; cursor:pointer">Back to Admin Dashboard</a>
            </div>
        '''
        return AppFrame.render(inner_html, user=user)
    
    @staticmethod
    # Renders the order details for a specific order
    def render_details(order_num, items, user=None):
        # Determine redirection based on user role (as admin and customer can both access this)
        if isinstance(user, AdministratorAccount):
            back_url = "/shipping"
            back_text = "Back to Shipment Management"
        else: 
            back_url = "/order"
            back_text = "Back to Order History"

        rows = ""
        total_price = 0
        for i in items:
            subtotal = i['quantity'] * i['price']
            total_price += subtotal
            rows += f'''
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align:left;">{i['isbn']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align:left;">{i['title']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align:left;">{i['author']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align:right;">{i['quantity']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align:right;">${i['price']:.2f}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align:right;">${subtotal:.2f}</td>
            </tr>
            '''
        
        inner_html = f'''
            <h2>Order Details: {order_num}</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #f5f5f5;">
                    <th style="padding: 10px; text-align:left;">ISBN</th>
                    <th style="padding: 10px; text-align:left;">Title</th>
                    <th style="padding: 10px; text-align:left;">Author</th>
                    <th style="padding: 10px; text-align:right;">Qty</th>
                    <th style="padding: 10px; text-align:right;">Price</th>
                    <th style="padding: 10px; text-align:right;">Total</th>
                </tr>
                {rows}
            </table>
            <p style="text-align: right;">Final Total: ${total_price:.2f}</p>
            <div style="text-align: center; margin-top:20px;">
                <a href="{back_url}" style="display:inline-block; padding: 10px 20px; text-decoration: none; background: #333; color:#fff; border:none; cursor:pointer">{back_text}</a>
            </div>
        '''
        return AppFrame.render(inner_html, user=user)

        