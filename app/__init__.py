from flask import Flask

app = Flask(__name__)
app.json.sort_keys = False  # from stackoverflow to avoid default alphabetical order
USERS = []
POSTS = []

from app import views_all, views
from app import models

# todo how import works in python
#   как работают модули
#  что считается модулем в питоне
#  запускаются ли все приложения при импорте?
# todo why directory with __init__.py works as module, области видимости
