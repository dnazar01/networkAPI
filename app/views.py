from flask import jsonify, request, Response
from http import HTTPStatus

from app import app  # ссылка на объект с названием app, созданный в __init__
from app import USERS, POSTS
from app.models import User, Post


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


@app.post('/posts/create')
def create_post():
    author_id = request.json.get('author_id')
    text = request.json.get('text')
    if 0 <= author_id < len(USERS):
        post = Post(len(POSTS), author_id, text)
        USERS[author_id].posts.append(post.post_id)
        POSTS.append(post)
        return jsonify(id=post.post_id, author_id=post.author_id, text=post.text, reactions=post.reactions)
    return Response(status=HTTPStatus.BAD_REQUEST)


@app.route('/posts/<int:post_id>')
def get_post(post_id):
    if 0 <= post_id < len(POSTS):
        post = POSTS[post_id]
        return jsonify(id=post.post_id, author_id=post.author_id, text=post.text, reactions=post.reactions)
    return Response(status=HTTPStatus.BAD_REQUEST)


@app.post('/posts/<int:post_id>/reaction')
def post_reaction(post_id):
    user_id = request.json.get('user_id')
    reaction = request.json.get('reaction')
    if 0 <= user_id < len(USERS) and 0 <= post_id < len(POSTS):
        post = POSTS[post_id]
        post.add_reaction(reaction)
        return Response(status=HTTPStatus.OK)
    return Response(status=HTTPStatus.BAD_REQUEST)
