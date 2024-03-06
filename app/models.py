import re
from app import USERS


class User:
    def __init__(self, id, first_name, last_name, email, total_reactions=0, posts=None):
        if posts is None:
            posts = []
        self.id = id
        self.firstName = first_name
        self.lastName = last_name
        self.email = email
        self.totalReactions = total_reactions
        self.posts = posts

    @staticmethod
    def is_email_valid(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(pattern, email):
            return True
        else:
            return False


class Post:
    def __init__(self, post_id, author_id, text):
        self.post_id = post_id
        self.author_id = author_id
        self.text = text
        self.reactions = []

    def add_reaction(self, reaction):
        self.reactions.append(reaction)
        USERS[self.author_id].totalReactions += 1
