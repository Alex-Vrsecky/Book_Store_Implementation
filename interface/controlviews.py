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
        inner_html = '''
            <h2>Your Account</h2>
            <p>Welcome back, <strong>{{ self.username }}</strong></p>
            <hr>
            <ul>
                <li><a href="/catalogue">Browse Book Catalogue</a></li>
                <li><a href="/cart">View Shopping Cart</a></li>
                <li><a href="/logout">Logout</a></li>
            </ul>
        '''
        return AppFrame.render(inner_html, user=self)


class AdministratorAccount(Account):
    # render an admin dashboard at /dashboard
    def render_dashboard(self):
        inner_html = '''
            <h2>Admin Portal</h2>
            <p>Staff ID Identity: <strong>{{ self.username }}</strong></p>
            <p>Security Clearance: Multi-Factor Confirmed</p>
            <hr>
            <ul>
                <li><a href="/stock">Update Inventory Stock Levels</a></li>
                <li><a href="/catalogue/manage">Add/Remove Books</a></li>
                <li><a href="/logout">Logout</a></li>
            </ul>
        '''
        return AppFrame.render(inner_html, user=self)
        
class Catalogue:
    @staticmethod
    # render the catalogue/hompage components
    def render(books, user=None, current_search="", current_author=""):
        # Individual book HTML !!! MUST MOVE TO BOOK CLASS !!!
        books_html = "".join([
            f'<div style="border:1px solid #ccc; padding:10px; margin:5px; border-radius:4px;">'
            f'<h3>{b["title"]}</h3>'
            f'<p><strong>Author:</strong> {b.get("author", "Unknown")}</p>'
            f'<p>Price: ${b["price"]}</p></div>' 
            for b in books
        ])
        # move to book class ^^^
        
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