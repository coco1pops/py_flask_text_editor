from flask_login import UserMixin
from editor import login_manager
from editor import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self,user_id, user_password, user_name, user_role ):
        self.id = user_id
        self.password_hash=user_password
        self.user_name=user_name
        self.user_role=user_role
        self.is_admin=(self.user_role=="Admin")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
@login_manager.user_loader
def load_user(user_id):
    user_record=db.get_user(user_id)
    user=User(user_record['user_id'], user_record['user_password'], user_record['user_name'], user_record['user_role'])
    return user
