from flask import Flask

app = Flask(__name__)

from app import views

# todo how import works in python
#   как работают модули
#  что считается модулем в питоне
#  запускаются ли все приложения при импорте?
# todo why directory with __init__.py works as module, области видимости и почему app
