from flask import Flask

app = Flask(__name__)
app.json.sort_keys = False  # from stackoverflow to avoid default alphabetical order
USERS = []
POSTS = []

from app import views_all, views
from app import models
