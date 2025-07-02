from flask_login import login_user, UserMixin

class CKANUser(UserMixin):
    def __init__(self, name):
        self.id = name

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
