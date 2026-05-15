from editor.models.database import db, print_except
from editor.models.storyChars import StoryCharsService
from editor.models.chapters import ChapterCharService

from datetime import datetime
from flask_login import current_user
import base64

class Char(db.Model):
    __tablename__ = "chars"

    char_id = db.Column(db.Integer, primary_key=True)
    created = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    personality = db.Column(db.Text)
    motivation = db.Column(db.Text)
    image_data = db.Column(db.LargeBinary)
    image_mime_type = db.Column(db.Text)
    user_id = db.Column(db.String(255), db.ForeignKey('users.user_id'), nullable=False)

class CharService:
    @staticmethod
    def get_characters():
        try:
            return Char.query.filter_by(user_id=current_user.id).all()
        except Exception as e:
            print_except("get_characters",e)
            return False
        
    @staticmethod
    def get_character(char_id, allow_not_found=False):
        try:
            char = Char.query.filter_by(char_id=char_id, user_id=current_user.id).first()

            if not char and not allow_not_found:
                print_except("get_character","Record not found")

            return char
        
        except Exception as e:
            print_except("get_character",e)

    @staticmethod
    def get_character_formatted(char_id, allow_not_found=False):
        try:
            char = Char.query.filter_by(char_id=char_id, user_id=current_user.id).first()

            if not char and not allow_not_found:
                print_except("get_character","Record not found")

            format_image_data=None
            if char.image_mime_type and char.image_data:
                format_image_data = "data:" + char.image_mime_type + ";base64," + base64.b64encode(char.image_data).decode('utf-8') 

            return {
                "char_id": char.char_id,
                "name": char.name,
                "description": char.description,
                "personality": char.personality,
                "motivation": char.motivation,
                "image_data": format_image_data,
                "image_mime_type": char.image_mime_type
            }

        except Exception as e:
            print_except("get_character_formatted",e)   

    @staticmethod
    def get_characters_outside_story(story_id):
        assigned_ids = StoryCharsService.get_assigned_char_subquery(story_id)
        try:
           available_chars = Char.query.filter(Char.user_id == current_user.id, ~Char.char_id.in_(assigned_ids)).all()
           return available_chars
        
        except Exception as e:
            print_except("get_characters_outside_story",e)
            return False

    @staticmethod
    def get_characters_outside_chapter(story_id, chapter_id):
        assigned_ids = ChapterCharService.get_assigned_char_subquery(story_id, chapter_id)
        try:
           available_chars = Char.query.filter(Char.user_id == current_user.id, ~Char.char_id.in_(assigned_ids)).all()
           return available_chars
        
        except Exception as e:
            print_except("get_characters_outside_chapter",e)
            return False


    @staticmethod
    def insert_character(name, description, personality, motivation):
        try:
            char = Char(
                name=name,
                description=description,
                personality=personality,
                motivation=motivation,
                user_id=current_user.id
            )

            db.session.add(char)
            db.session.commit()

            return char.char_id  # works for BOTH SQLite & Postgres
    
        except Exception as e:
            db.session.rollback()
            print_except("insert_character",e)

    @classmethod
    def update_character_field(cls, char_id, field, value):
        try:
            char = cls.get_character(char_id, allow_not_found=False)

            if not char:
                return False

            setattr(char, field, value)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            print_except("update_character_field",e)

    @classmethod
    def update_character_all(cls, char_id, name, description, personality, motivation):
        try:
            char = cls.get_character(char_id, allow_not_found=False)

            if not char:
                return False

            char.name = name
            char.description = description
            char.personality = personality
            char.motivation = motivation

            db.session.commit()
            return True
        
        except Exception as e:
            db.session.rollback()
            print_except("update_character_all",e)

    @classmethod
    def update_character_image(cls, char_id, image_data, image_mime_type):
        try:
            char = cls.get_character(char_id, allow_not_found=False)

            if not char:
                return False

            char.image_data = image_data
            char.image_mime_type = image_mime_type

            db.session.commit()
            return True
        
        except Exception as e:
            db.session.rollback()
            print_except("update_character_image",e)

    @classmethod
    def delete_character(cls, char_id):
        try:
            char = cls.get_character(char_id, allow_not_found=False)

            if not char:
                return False

            db.session.delete(char)
            db.session.commit()
            return True
        
        except Exception as e:
            db.session.rollback()
            print_except("delete_character",e)


    @classmethod
    def build_char(cls,char_id):
        char = cls.get_character_formatted(char_id, allow_not_found=False)

        resp={"img": "", "image_mime_type" : "", "text" : ""}
        if char['image_mime_type']:
            resp["image_mime_type"] = char['image_mime_type']
            resp["img"] = char["image_data"]
            resp["text"] = f"The picture shows <b>{char['name']}</b><br>"

        if char["description"] != "":
            resp["text"] = f"{resp['text']}<b>Description</b><br> {char['description']}"

        if char["personality"] != "":
            resp["text"] = f"{resp['text']}<br><b>Personality</b><br> {char['personality']}"

        if char["motivation"] != "":
            resp["text"] = f"{resp['text']}<br><b>Motivation</b><br> {char['motivation']}"
        
        return resp