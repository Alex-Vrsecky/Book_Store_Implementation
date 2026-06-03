# app.py
from flask import Flask, request, make_response, redirect
import os

from server import Database, LoginController, CatalogueController
from interface import *
from app_frame import AppFrame

app = Flask(__name__)

SHARED_KEY = os.environ.get("SECRET_KEY", os.urandom(32))
database = Database()
login_model = LoginController(database, SHARED_KEY)
catalogue_model = CatalogueController(database, SHARED_KEY)

#ESTABLISH TOKEN STATUS
def get_authenticated_user():
    token = request.cookies.get('session_token')
    if token:
        payload = login_model.verify_session_token(token)
        if payload:
            username = payload.get('username')
            role = payload.get('role')
            if role == 'admin':
                return AdministratorAccount(username)
            return CustomerAccount(username)
    return None

@app.route('/')
def home():
    return redirect('/catalogue')

@app.route('/login', methods=['GET', 'POST']) # 1. Allow both GET and POST
def login():
    # Render form
    if request.method == 'GET':
        login_form_html = '''
            <h2>Online Bookstore Portal</h2>
            <form action="/login" method="POST">
                Username: <input type="text" name="username" required><br><br>
                Password: <input type="password" name="password" required><br><br>
                <input type="submit" value="Login">
            </form>
        '''
        return AppFrame.render(login_form_html, user=None)

    # handle form submission
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        return login_model.validate_credentials(username, password)

@app.route('/dashboard')
def dashboard():
    user = get_authenticated_user()
    token = request.cookies.get('session_token')
    
    # use appropriate view for admin or customer
    if user and token:
        return user.render_dashboard(token)
        
    # missing token catch
    return redirect('/login')
    
@app.route('/catalogue')
def catalogue(): 
    user = get_authenticated_user()
    books = catalogue_model.get_all_books()
    return Catalogue.render(books, user=user)

@app.route('/logout')
def logout():
    response = make_response(redirect('/'))
    response.set_cookie('session_token', '', expires=0)
    return response

if __name__ == '__main__':
    app.run(port=5000, debug=True)