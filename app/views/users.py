from flask import jsonify, request, Response
from http import HTTPStatus
import matplotlib.pyplot as plt
from app import app, USERS
from app.models import User


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
