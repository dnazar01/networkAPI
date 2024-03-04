class User:
    def __init__(self, id, first_name, last_name, email, total_reactions=0, posts=[]):
        self.id = id
        self.firstName = first_name
        self.lastName = last_name
        self.email = email
        self.totalReactions = total_reactions
        self.posts = posts
