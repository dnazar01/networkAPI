from flask import jsonify, request, Response
from http import HTTPStatus
from app import app, USERS, POSTS
from app.models import Post, User
from app.enum_classes import Status, SortType


@app.post("/posts/create")
def create_post():
    author_id = request.json.get("author_id")
    text = request.json.get("text")
    if not User.is_valid_id(author_id):
        return Response(status=HTTPStatus.BAD_REQUEST)
    post = Post(len(POSTS), author_id, text)
    USERS[author_id].posts.append(post.post_id)
    POSTS.append(post)
    return jsonify(
        id=post.post_id,
        author_id=post.author_id,
        text=post.text,
        reactions=post.reactions,
    )


@app.route("/posts/<int:post_id>")
def get_post(post_id):
    if not Post.is_valid_id(post_id):
        return Response(status=HTTPStatus.BAD_REQUEST)
    post = POSTS[post_id]
    return jsonify(
        id=post.post_id,
        author_id=post.author_id,
        text=post.text,
        reactions=post.reactions,
    )


@app.post("/posts/<int:post_id>/reaction")
def post_reaction(post_id):
    user_id = request.json.get("user_id")
    reaction = request.json.get("reaction")
    if not (User.is_valid_id(user_id) and Post.is_valid_id(post_id)):
        return Response(status=HTTPStatus.BAD_REQUEST)
    post = POSTS[post_id]
    post.add_reaction(reaction)
    return Response(status=HTTPStatus.OK)


@app.route("/users/<int:user_id>/posts")
def get_all_user_posts(user_id):
    sort_type = request.json.get("sort")  # asc/desc
    if not User.is_valid_id(user_id):
        return Response(status=HTTPStatus.BAD_REQUEST)
    user = USERS[user_id]  # check validity # создаем новый массив, ссылаемся на POSTS

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
    if sort_type == SortType.ASCENDING.value:
        return jsonify(posts=user_posts)
    if sort_type == SortType.DESCENDING.value:
        return jsonify(posts=user_posts[::-1])


@app.delete("/posts/<int:post_id>")
def delete_post(post_id):
    if not Post.is_valid_id(post_id):
        return Response(status=HTTPStatus.BAD_REQUEST)
    post = POSTS[post_id]
    post.status = Status.DELETED.value
    return jsonify(
        id=post.post_id,
        author_id=post.author_id,
        text=post.text,
        reactions=post.reactions,
        status=post.status,
    )
