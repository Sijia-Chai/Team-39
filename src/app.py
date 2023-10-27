import google.oauth2.id_token as id_token
import google
import pip._vendor.cachecontrol as cachecontrol
import os
import pathlib
from google_auth_oauthlib.flow import Flow
from flask import *
from api_keys import *
from methods import *
import flask
import requests
import flask_login
import webbrowser
from flaskext.mysql import MySQL
import re
import sqlite3
import os.path

app = Flask(__name__)
app.secret_key = flask_app_secret