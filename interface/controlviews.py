# controlviews.py
from app_frame import AppFrame
from flask import render_template_string
# accounts.py (Top of the file)

def render_page_layout(title, username, role, main_content):
    """UI general formatting"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Bookstore</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-50 font-sans text-slate-800 antialiased min-h-screen flex flex-col">
        
        <nav class="bg-slate-900 text-white shadow-md px-6 py-4 flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <span class="text-xl font-bold tracking-tight text-blue-400">📚 SecureBookstore</span>
                <span class="bg-slate-800 text-xs px-2.5 py-1 rounded-full border border-slate-700 text-slate-300 font-mono">{role} Portal</span>
            </div>
            <div class="flex items-center space-x-6">
                <span class="text-sm text-slate-300">Welcome, <strong class="text-white">{username}</strong></span>
                <a href="/logout" class="bg-red-500/10 hover:bg-red-500 hover:text-white text-red-400 px-3.5 py-1.5 rounded-lg text-sm font-medium transition duration-150 ease-in-out border border-red-500/20">
                    Logout
                </a>
            </div>
        </nav>

        <main class="flex-grow max-w-7xl w-full mx-auto p-6 md:p-8">
            {main_content}
        </main>

        <footer class="bg-slate-100 border-t border-slate-200 text-center py-4 text-xs text-slate-500 font-mono">
            SWE30003 Assignment Proof-of-Concept System Validation • 2026 Session
        </footer>
    </body>
    </html>
    """
    
class Account:
    def __init__(self, username):
        self.username = username

    def render_dashboard(self, token):
        raise NotImplementedError("Subclasses must render their own views.")


class CustomerAccount(Account):
    def render_dashboard(self, token):
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
    def render_dashboard(self, token):
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
    def render(books, user=None, current_search="", current_author=""):
        # Individual book HTML !!!MUST MOVE TO BOOK CLASS
        books_html = "".join([
            f'<div style="border:1px solid #ccc; padding:10px; margin:5px; border-radius:4px;">'
            f'<h3>{b["title"]}</h3>'
            f'<p><strong>Author:</strong> {b.get("author", "Unknown")}</p>'
            f'<p>Price: ${b["price"]}</p></div>' 
            for b in books
        ])
        
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