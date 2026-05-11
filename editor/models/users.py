from editor.models.database import db, print_except

from werkzeug.security import generate_password_hash
from sqlalchemy import Enum

import logging

class Usr(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.String(255), primary_key=True)
    user_password = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.String(50), Enum("Standard", "Admin", name="role_enum"), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)

class UserService:

    @staticmethod
    def get_user( user_id, allow_not_found=False):
        try:
            user = db.session.get(Usr, user_id)

            if not user and not allow_not_found:
                print_except("get_user", "Record not found")

            return user
        except Exception as e:
            print_except("get_user", e)
    
    @staticmethod
    def get_users():
        try:
            return Usr.query.all()
        except Exception as e:
            print_except("get_users", e)

    @staticmethod
    def insert_user( user_id, user_password, user_name, user_role):
        try:
            user = Usr(
                user_id=user_id,
                user_password=user_password,
                user_name=user_name,
                user_role=user_role
            )

            db.session.add(user)
            db.session.commit()

            return user.user_id  # works for BOTH SQLite & Postgres
    
        except Exception as e:
            db.session.rollback()
            print_except("insert_user", e)

    @classmethod
    def update_user(cls, user_id, user_name, user_role):
        try:
            user = cls.get_user(user_id)

            if not user:
                return False

            user.user_name = user_name
            user.user_role = user_role

            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            print_except("update_user", e)

    @classmethod
    def user_reset_pass(cls, user_id, new_password):
        try:
            user=cls.get_user(user_id)

            if not user:
                return False

            hash_password = generate_password_hash(new_password)
            user.user_password = hash_password

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print_except("user_reset_pass", e)    

    @classmethod
    def delete_user(cls, user_id):
        try:
            user = cls.get_user(user_id)
            if not user:
                return False
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print_except("delete_user", e)  

    @classmethod
    def check_admin_user(cls):
        try:
            admin_user = Usr.query.filter_by(user_role="Admin").first()
            if not admin_user:
                logging.debug("No admin user found, creating default admin user")
                cls.insert_user("admin", "admin123", "Admin User", "Admin")
                cls.user_reset_pass("admin", "admin123")
                logging.debug("Default admin user created successfully")
            else:
                logging.debug(f"Admin user found: {admin_user.user_name}")
        except Exception as e:
            print_except("check_admin_user", e)

    @staticmethod
    def checkSU():
        try:
            su_user = Usr.query.filter_by(user_role="Admin").first()
            if su_user:
                logging.debug(f"DB - Superuser found: {su_user.user_name}")
                return True
            else:
                logging.debug("DB - No superuser found")
                return False
        except Exception as e:
            print_except("checkSU", e)