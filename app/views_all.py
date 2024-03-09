from app import app  # ссылка на объект с названием app, созданный в __init__
from app import USERS, POSTS


@app.route("/")
def index():
    return f"<h1>Hello World!</h1><br>{USERS}</br><br>{POSTS}</br>"
