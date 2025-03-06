from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = generate_password_hash(password)

    @staticmethod
    def get(username):
        # This is a simple in-memory user store. In a real application, you'd use a database.
        users = {
            'admin': User(1, 'admin', 'Pro123!'),
        }
        return users.get(username)

    @staticmethod
    def get_by_id(user_id):
        # This is a simple in-memory user store. In a real application, you'd use a database.
        users = {
            1: User(1, 'admin', 'Pro123!'),
        }
        return users.get(user_id)

    def check_password(self, password):
        return check_password_hash(self.password, password)