def create_post_payload():
    return {
        "author_id": 0,
        "text": "sample text",
    }


def create_user_payload():
    return {
        "first_name": "Vasya",
        "last_name": "Gubkin",
        "email": "test@mail.ru"
    }


def create_reaction_payload():
    return {
        "user_id": 0,
        "reaction": "boom"
    }
