from flask import render_template_string
# This is purely dynamically generated HTML that acts as a frame for the website
#  Elements that are always on screen (ie. navbar) are rendered here
class AppFrame:
    @staticmethod
    def render(content_html, user=None):
        # Dynamic navigation button based on whether user is logged in
        if user:
            nav_button = f'<a href="/dashboard" style="color: #4CAF50;">{user.username} (Account)</a>'
        else:
            nav_button = '<a href="/login">Login</a>'

        # The global "Outer Frame"
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>TFB Bookstore</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                    nav { background: #333; color: white; padding: 15px; display: flex; justify-content: space-between; }
                    nav a { color: white; text-decoration: none; margin-left: 15px; }
                    .container { padding: 20px; }
                </style>
            </head>
            <body>
                <nav>
                    <strong>TFB</strong>
                    <div>
                        <a href="/catalogue">Catalogue</a>
                        {{ nav_button|safe }}
                    </div>
                </nav>
                <div class="container">
                    {{ content_html|safe }}
                </div>
            </body>
            </html>
        ''', nav_button=nav_button, content_html=content_html)