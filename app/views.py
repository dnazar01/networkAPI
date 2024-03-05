from flask import jsonify, request, Response
from http import HTTPStatus
from app.models import User

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
    if User.is_email_valid(email):
        user = User(len(USERS), first_name, last_name, email)
        USERS.append(user)
        # todo check email for validity
        return jsonify(id=user.id, first_name=user.firstName, last_name=user.lastName, email=user.email,
                       total_reactions=user.totalReactions, posts=user.posts)
    return Response(status=HTTPStatus.BAD_REQUEST)


@app.route('/users/<int:user_id>')
def get_user(user_id):
    if user_id < 0 or user_id >= len(USERS):
        return Response(status=HTTPStatus.BAD_REQUEST)
    user = USERS[user_id]
    return jsonify(id=user.id, first_name=user.firstName, last_name=user.lastName, email=user.email,
                   total_reactions=user.totalReactions, posts=user.posts)
