from flask import jsonify, request, Response
from http import HTTPStatus
import matplotlib.pyplot as plt
from app import app, USERS, POSTS
from app.models import User
from app.enum_classes import Status, SortType


@app.post("/users/create")
def create_user():
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    email = request.json.get("email")
    if not User.is_email_valid(email):
        return Response(status=HTTPStatus.BAD_REQUEST)
    user = User(len(USERS), first_name, last_name, email)
    USERS.append(user)
    return jsonify(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        total_reactions=user.total_reactions,
        posts=user.posts,
    )



@app.route("/users/<int:user_id>")
def get_user(user_id):
    if not User.is_valid_id(user_id):
        return Response(status=HTTPStatus.BAD_REQUEST)
    user = USERS[user_id]
    return jsonify(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        total_reactions=user.total_reactions,
        posts=user.posts,
    )



@app.route("/users/leaderboard")
def get_users_leaderboard():
    output_data_type = request.json.get("type")  # list/graph
    sort_type = request.json.get("sort")  # asc/desc
    if output_data_type == "list":
        leaderboard_list = [
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "total_reactions": user.total_reactions,
            }
            for user in USERS
            if User.is_valid_id(user.id)
        ]
        leaderboard_list.sort(key=lambda user: user["total_reactions"])
        if sort_type == SortType.ASCENDING.value:
            return jsonify(users=leaderboard_list)
        elif sort_type == SortType.DESCENDING.value:
            return jsonify(users=leaderboard_list[::-1])
    if output_data_type == "graph":
        leaderboard_list = [
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "total_reactions": user.total_reactions,
            }
            for user in USERS
            if User.is_valid_id(user.id)
        ]
        fig, ax = plt.subplots()

        users = [
            f"{user['first_name']} {user['last_name']} ({user['id']})"
            for user in leaderboard_list
        ]
        reacts = [user["total_reactions"] for user in leaderboard_list]

        ax.bar(users, reacts)

        ax.set_ylabel("User score")
        ax.set_title("User leaderboard by reactions")

        plt.savefig("app/static/images/leaderboard.png")
        return Response(
            '<img src="static/images/leaderboard.png">',
            status=HTTPStatus.OK,
            mimetype="text/html",
        )
    return Response(status=HTTPStatus.BAD_REQUEST)


@app.delete("/users/<int:user_id>")
def delete_user(user_id):
    if not User.is_valid_id(user_id):
        return Response(status=HTTPStatus.BAD_REQUEST)
    user = USERS[user_id]
    user.status = Status.DELETED.value
    return jsonify(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        total_reactions=user.total_reactions,
        posts=user.posts,
        status=user.status,
    )
