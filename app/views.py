from flask import jsonify, request, Response
from http import HTTPStatus
import matplotlib.pyplot as plt

from app import app  # ссылка на объект с названием app, созданный в __init__
from app import USERS, POSTS
from app.models import User, Post


@app.route("/")
def index():
    return "<h1>Hello World!</h1>"


@app.post("/users/create")
def create_user():
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    email = request.json.get("email")
    if User.is_email_valid(email):
        user = User(len(USERS), first_name, last_name, email)
        USERS.append(user)
        return jsonify(
            id=user.id,
            first_name=user.firstName,
            last_name=user.lastName,
            email=user.email,
            total_reactions=user.totalReactions,
            posts=user.posts,
        )
    return Response(status=HTTPStatus.BAD_REQUEST)


@app.route("/users/<int:user_id>")
def get_user(user_id):
    if 0 <= user_id < len(USERS):
        user = USERS[user_id]
        return jsonify(
            id=user.id,
            first_name=user.firstName,
            last_name=user.lastName,
            email=user.email,
            total_reactions=user.totalReactions,
            posts=user.posts,
        )
    return Response(status=HTTPStatus.BAD_REQUEST)


@app.post("/posts/create")
def create_post():
    author_id = request.json.get("author_id")
    text = request.json.get("text")
    if 0 <= author_id < len(USERS):
        post = Post(len(POSTS), author_id, text)
        USERS[author_id].posts.append(post.post_id)
        POSTS.append(post)
        return jsonify(
            id=post.post_id,
            author_id=post.author_id,
            text=post.text,
            reactions=post.reactions,
        )
    return Response(status=HTTPStatus.BAD_REQUEST)


@app.route("/posts/<int:post_id>")
def get_post(post_id):
    if 0 <= post_id < len(POSTS):
        post = POSTS[post_id]
        return jsonify(
            id=post.post_id,
            author_id=post.author_id,
            text=post.text,
            reactions=post.reactions,
        )
    return Response(status=HTTPStatus.BAD_REQUEST)


@app.post("/posts/<int:post_id>/reaction")
def post_reaction(post_id):
    user_id = request.json.get("user_id")
    reaction = request.json.get("reaction")
    if 0 <= user_id < len(USERS) and 0 <= post_id < len(POSTS):
        post = POSTS[post_id]
        post.add_reaction(reaction)
        return Response(status=HTTPStatus.OK)
    return Response(status=HTTPStatus.BAD_REQUEST)


@app.route("/users/<int:user_id>/posts")
def get_user_posts_sorted(user_id):
    sort_type = request.json.get("sort")  # asc/desc
    if 0 <= user_id < len(USERS):
        user = USERS[
            user_id
        ]  # check validity # создаем новый массив, ссылаемся на POSTS

        user_posts = [
            {
                "id": POSTS[post_id].post_id,
                "author_id": POSTS[post_id].author_id,
                "text": POSTS[post_id].text,
                "reactions": POSTS[post_id].reactions,
            }
            for post_id in user.posts
        ]

        user_posts.sort(
            key=lambda post: len(post["reactions"])
        )  # создаем новый массив, версию старого сортированного по реакциям
        if sort_type == "asc":
            return jsonify(posts=user_posts)
        if sort_type == "desc":
            return jsonify(posts=user_posts[::-1])
    return Response(status=HTTPStatus.BAD_REQUEST)


@app.route("/users/leaderboard")
def get_users_leaderboard():
    output_data_type = request.json.get("type")  # list/graph
    sort_type = request.json.get("sort")  # asc/desc
    if output_data_type == "list":
        leaderboard_list = [
            {
                "id": user.id,
                "first_name": user.firstName,
                "last_name": user.lastName,
                "email": user.email,
                "total_reactions": user.totalReactions,
            }
            for user in USERS
        ]
        leaderboard_list.sort(key=lambda user: user["total_reactions"])
        if sort_type == "asc":
            return jsonify(users=leaderboard_list)
        if sort_type == "desc":
            return jsonify(users=leaderboard_list[::-1])
    if output_data_type == "graph":
        leaderboard_list = [
            {
                "id": user.id,
                "first_name": user.firstName,
                "last_name": user.lastName,
                "total_reactions": user.totalReactions,
            }
            for user in USERS
        ]
        fig, ax = plt.subplots()

        users = [f"{user['first_name']} {user['last_name']} ({user['id']})" for user in leaderboard_list]
        reacts = [user['total_reactions'] for user in leaderboard_list]

        ax.bar(users, reacts)

        ax.set_ylabel('User score')
        ax.set_title('User leaderboard by reactions')

        plt.savefig('app/static/images/leaderboard.png')
        return Response('<img src="static/images/leaderboard.png">', status=HTTPStatus.OK, mimetype="text/html")
    return Response(status=HTTPStatus.BAD_REQUEST)
