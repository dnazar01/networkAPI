from flask import jsonify, request
from models import User

from app import app  # ссылка на объект с названием app, созданный в __init__
from app import USERS


@app.route('/')
def index():
    return "<h1>Hello World!</h1>"


@app.post('/users/create')
def create_user():
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    email = request.json.get('email')
    user = User(len(USERS), first_name, last_name, email)
    USERS.append(user)
    # todo check email for validity
    return jsonify(user)
