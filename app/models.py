import re
from app import USERS, POSTS
from app.enum_classes import Status


class User:
    def __init__(self, id, first_name, last_name, email, total_reactions=0):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.total_reactions = total_reactions
        self.posts = []
        self.status = Status.CREATED.value

    @staticmethod
    def is_email_valid(email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(pattern, email):
            return True
        else:
            return False

    @staticmethod
    def is_valid_id(user_id):
        return 0 <= user_id < len(USERS) and USERS[user_id].status != Status.DELETED.value


class Post:
    def __init__(self, post_id, author_id, text):
        self.post_id = post_id
        self.author_id = author_id
        self.text = text
        self.reactions = []
        self.status = Status.CREATED.value

    def add_reaction(self, reaction):
        self.reactions.append(reaction)
        USERS[self.author_id].total_reactions += 1

    @staticmethod
    def is_valid_id(post_id):
        return 0 <= post_id < len(POSTS) and POSTS[post_id].status != Status.DELETED.value
