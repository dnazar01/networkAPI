def create_post_payload():
    return {
        "author_id": 0,
        "text": "sample text",
    }


def create_user_payload():
    return {"first_name": "Vasya", "last_name": "Gubkin", "email": "test@mail.ru"}


def create_reaction_payload():
    return {"user_id": 0, "reaction": "boom"}


def to_specific_dict(dictionary, *args):
    new_dict = {}
    for key in args:
        new_dict[key] = dictionary[key]
    return new_dict
