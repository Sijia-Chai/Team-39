import google.oauth2.id_token as id_token
import google
import pip._vendor.cachecontrol as cachecontrol
import os
import pathlib
from google_auth_oauthlib.flow import Flow
from flask import *
from api_keys_public import *
from methods import *
import flask
import requests
import flask_login
import webbrowser
import mysql.connector
import re
import sqlite3
import os.path

app = Flask(__name__)
app.secret_key = flask_app_secret

# Database
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

def database_initialize():
    conn = sqlite3.connect('./database.db')
    c = conn.cursor()
    c.execute("""
       CREATE TABLE users (
           user_id int4 AUTO_INCREMENT,
           email varchar(255) UNIQUE NOT NULL,
           password varchar(255) NOT NULL,
           first_name varchar(255) NOT NULL,
           last_name varchar(255) NOT NULL,
           PRIMARY KEY (user_id) 
           )""")
    conn.commit()
    conn.close()

def setup_database():
    if not os.path.isfile('./database.db'):
        database_initialize()

setup_database()
conn = sqlite3.connect('./database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("SELECT email FROM users")
users = cursor.fetchall()

def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users")
    return cursor.fetchall()

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    try:
        users = getUserList()
        email = request.form.get('email')
        if not(email) or email not in str(users):
            return
        user = User()
        user.id = email
        conn = sqlite3.connect('./database.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE email = '{0}'".format(email))
        data = cursor.fetchall()
        pwd = str(data[0][0])
        request.form['password'] == pwd
        return user
    except:
        return None

# GOOGLE Login
client_id_google = google_id
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
client_secret_file = os.path.join(pathlib.Path(
    __file__).parent, "client_secret_google.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secret_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

def require_google_login(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
        return wrapper()

@app.route('/google_login')
def google_login():
    auth_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(auth_url)

@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)
    creds = flow.credentials
    request_sess = requests.session()
    cached_sess = cachecontrol.CacheControl(request_sess)
    token_req = google.auth.transport.requests.Request(session=cached_sess)
    id_data = id_token.verify_oauth2_token(
        id_token=creds._id_token,
        request=token_req,
        audience=client_id_google
    )
    session["google_id"] = id_data.get("sub")
    session["name"] = id_data.get("name")
    return redirect("/protected_area")

@app.route('/google_logout')
def google_logout():
    session.clear()
    return redirect("/")

@app.route('/google_login')
def index():
    session["google_id"] = "Test"
    return flask.redirect("/protected_area")

@require_google_login
@app.route('/protected_area')
def protected_area():
    return redirect("/")

# Email Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')
    email = flask.request.form['email']
    conn = sqlite3.connect('./database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users")
    rows = cursor.fetchall()
    checkEmail = flask.request.form['email']
    for x in rows:
        formatX = str(x)[2:-3]
        if checkEmail == formatX:
            if cursor.execute("SELECT password FROM users WHERE email = '{0}'".format(email)):
                data = cursor.fetchall()
                pwd = str(data[0][0])
                if flask.request.form['password'] == pwd:
                    user = User()
                    user.id = email
                    flask_login.login_user(user) 
                    return flask.redirect(flask.url_for('protected'))
    return render_template('unauth.html')

@app.route('/logout')
def logout():
    session.clear()
    flask_login.logout_user()
    return render_template('home.html')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

# Registration
@app.route("/register", methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'first_name' in request.form and 'last_name' in request.form:
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        conn = sqlite3.connect('./database.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id FROM users WHERE email = '{0}'".format(email))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Oops, email address is invalid!'
        elif not re.match(r'[A-Za-z0-9]+', email):
            msg = 'Username can only havs character and number!'
        elif not email or not password or not email:
            msg = 'You need to fill out the blanks!'
        else:
            cursor.execute("INSERT INTO Users (email, password, first_name, last_name) VALUES ('{0}', '{1}', '{2}', '{3}')".format(
                email, password, first_name, last_name))
            conn.commit()
            msg = 'You have successfully registered!'
        return render_template('profile.html', name=email, msg=msg)

    elif request.method == 'POST':
        msg = 'You need to fill out the blanks!'
    return render_template('register.html', msg=msg)

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id FROM users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def isEmailUnique(email):
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM users WHERE email = '{0}'".format(email)):
        return False
    else:
        return True

@require_google_login
@app.route("/profile")
def protected():
    try:
        return render_template('profile.html', name=flask_login.current_user.id)
    except:
        return render_template("profile.html", name=session["name"])

# Google Maps
@app.route("/search", methods=['GET'])
def search():
    return render_template('search.html', supress='True')

@app.route('/search', methods=['POST'])
def CityPlans():
    try:
        print("HERE")
        response = call_map_api(request.form.get('city'))
        return render_template('destination.html', city=request.form.get('city'), responseThing=response)
    except:
        return render_template('search.html') + "<h3 style = \"color: #ff0000\">An error occurred for event recommendations</h3>"

# Weather
@app.route("/weather", methods=['GET'])
def weather():
    return render_template('weather.html', supress='True')

@app.route('/weather', methods=['POST'])
def weather_display():
    if request.method == 'POST':
        response = call_weather_api(request.form.get('city'))
        if response.status_code == 200:
            return render_template('weather_ret.html', city=request.form.get('city'), temperature=response.json()['main']['temp'], feels_like=response.json()['main']['feels_like'])
        else:
            return render_template('weather.html') + "<h3 style = \"color: #ff0000\">An error occurred for the weather</h3>"

@app.route("/")
def home():
    try:
        return render_template('profile.html') + "<h1 style = \"color: #0000ff\"> " + f"Welcome {session['name']}!" + "</h1>"
    except:
        return render_template('home.html') 

if __name__ == "__main__":
    webbrowser.open_new('http://127.0.0.1:5000/')
    app.run(port=5000, debug=True, use_reloader=False)
