from editor.models.database import db, print_except
from editor.models.chapters import ChapterCharService

from datetime import datetime

class StoryChars(db.Model):
    __tablename__ = "story_chars"

    id = db.Column(db.Integer, primary_key=True)
    char_id = db.Column(db.Integer, db.ForeignKey('chars.char_id'),)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.story_id'))
    note = db.Column(db.Text, nullable=True)

class StoryWithCharacters(db.Model):
    __tablename__ = "story_with_characters"

    story_id = db.Column(db.Integer)
    char_id = db.Column(db.Integer)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    note = db.Column(db.Text, nullable=True)
    motivation = db.Column(db.Text, nullable=True)
    personality = db.Column(db.Text, nullable=True)
    image_mime_type = db.Column(db.Text, nullable=True)
    image_data = db.Column(db.LargeBinary)
    image_description = db.Column(db.Text, nullable=True)

class StoryCharsService:
    @staticmethod
    def get_story_chars(story_id):
        try:
            return StoryChars.query.filter_by(story_id=story_id).all()
        except Exception as e:
            print_except("get_story_chars", e)

    @staticmethod
    def get_story_char(id):
        try:
            return StoryChars.query.filter_by(id=id).first()
        except Exception as e:
            print_except("get_story_chars", e)
    
    @staticmethod
    def get_story_chars_base(story_id, char_id):
        try:
            return StoryChars.query.filter_by(story_id=story_id, char_id=char_id).first()
        except Exception as e:
            print_except("get_story_chars", e)

    @staticmethod
    def get_story_chars_for_char(char_id):
        try:
            return StoryChars.query.filter_by(char_id=char_id).first()
        except Exception as e:
            print_except("get_story_chars", e)


    @staticmethod
    def insert_story_char(story_id, char_id, char_note):
        try:
            story_char = StoryChars(
                story_id=story_id,
                char_id=char_id,
                note=char_note
            )

            db.session.add(story_char)
            db.session.commit()

            return story_char.id  # works for BOTH SQLite & Postgres
    
        except Exception as e:
            db.session.rollback()
            print_except("insert_story_char", e)

    @classmethod
    def delete_story_char(cls, story_char_id):  
        try:
            story_char = db.session.get(StoryChars, story_char_id)

            if not story_char:
                print_except("delete_story_char", "Record not found")

            ChapterCharService.delete_chapter_chars_by_story(story_char.story_id,story_char.char_id)

            db.session.delete(story_char)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print_except("delete_story_char", e)
    
    @classmethod
    def update_story_char(cls, id, note):    
        try:
            story_char = cls.get_story_char(id)

            if not story_char:
                print_except("update_story_char", "Record not found")

            story_char.note = note
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print_except("update_story_char", e)

    @staticmethod
    def get_assigned_char_subquery(story_id):

        return db.session.query(StoryChars.char_id)\
            .filter_by(story_id=story_id)


class StoryWithCharactersService:
    @staticmethod
    def get_story_with_characters(story_id):
        try:
            return StoryWithCharacters.query.filter_by(story_id=story_id).all()
        except Exception as e:
            print_except("get_story_with_characters", e)

    @staticmethod
    def get_story_with_character(story_char_id,allow_not_found=False):
        try:
            story_char = StoryWithCharacters.query.filter_by(id=story_char_id).first()

            if not story_char:
                if allow_not_found:
                    return None
                print_except("get_story_with_character", "Record not found")
            return story_char
        except Exception as e:
            print_except("get_story_with_character", e)