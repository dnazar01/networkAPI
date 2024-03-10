from app import app  # ссылка на объект с названием app, созданный в __init__


@app.route("/")
def index():
    return f"<h1>Hello World!</h1>"
