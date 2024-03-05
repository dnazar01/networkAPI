import re


class User:
    def __init__(self, id, first_name, last_name, email, total_reactions=0, posts=[]):
        self.id = id
        self.firstName = first_name
        self.lastName = last_name
        self.email = email
        self.totalReactions = total_reactions
        self.posts = posts

    @staticmethod
    def is_email_valid(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        # Check if the email matches the pattern
        if re.match(pattern, email):
            return True
        else:
            return False


class Post:
    def __init__(self, id, author_id, text, reactions=[]):
        self.id = id
        self.author_id = author_id
        self.text = text
        self.reactions = reactions
