from editor.models.database import db, print_except

from datetime import datetime
from flask_login import current_user

class Story(db.Model):
    __tablename__ = "stories"

    story_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    note = db.Column(db.Text, nullable=True)
    systeminstruction = db.Column(db.Text, nullable=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    temperature = db.Column(db.Float, default=0.7)
    top_p = db.Column(db.Float, default=0.9)
    seed = db.Column(db.Integer, nullable=True)
    harassment_threshold = db.Column(db.String(255), nullable=True)
    hate_speech_threshold = db.Column(db.String(255), nullable=True)
    dangerous_content_threshold = db.Column(db.String(255), nullable=True)
    explicit_content_threshold = db.Column(db.String(255), nullable=True)
    model = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)


class StoryService:
    @staticmethod
    def get_story(story_id, allow_not_found=False):
        
        try:
            story = Story.query.filter_by(story_id=story_id, user_id=current_user.id).first()

            if not story and not allow_not_found:
                print_except("get_story", "Record not found")

            return story
        except Exception as e:
            print_except("get_story", e)

    @staticmethod
    def get_latest_story():
        try:
            return Story.query.filter_by(user_id=current_user.id).order_by(Story.created.desc()).first()
        except Exception as e:
            print_except("get_latest_story", e)
    
    @staticmethod
    def get_last_updated_story():
        try:
            return Story.query.filter_by(user_id=current_user.id).order_by(Story.updated.desc()).first()
        except Exception as e:
            print_except("get_last_updated_story", e)

    @staticmethod
    def insert_story(title, note, systeminstruction, temperature, top_p, harassment_threshold, hate_speech_threshold, dangerous_content_threshold, explicit_content_threshold, model):
        try:
            story = Story(
                title=title,
                note=note,
                systeminstruction=systeminstruction,
                temperature=temperature or 0.7,
                top_p=top_p or 0.9,
                harassment_threshold=harassment_threshold,
                hate_speech_threshold=hate_speech_threshold,
                dangerous_content_threshold=dangerous_content_threshold,
                explicit_content_threshold=explicit_content_threshold,
                model=model,
                user_id=current_user.id
            )

            db.session.add(story)
            db.session.commit()

            return story.story_id  # works for BOTH SQLite & Postgres
    
        except Exception as e:
            db.session.rollback()
            print_except("insert_story", e)

    @staticmethod
    def get_stories():
        try:
            return Story.query.filter_by(user_id=current_user.id).order_by(Story.created.desc()).all()
        except Exception as e:
            print_except("get_stories", e)  

    @classmethod   
    def delete_story(cls,story_id):
        try:
            story = cls.get_story(story_id)

            if not story:
                print_except("delete_story", "Record not found")

            db.session.delete(story)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print_except("delete_story", e)

    @classmethod
    def update_story(cls, story_id, field, value):
        try:
            story = cls.get_story(story_id)

            if not story:
                print_except("update_story", "Record not found")

            setattr(story, field, value)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print_except("update_story", e)

    @classmethod
    def touch_story(cls, story_id):
        try:
            story = cls.get_story(story_id)

            if not story:
                print_except("touch_story", "Record not found")

            story.updated = datetime.utcnow()

        except Exception as e:

            print_except("touch_story", e)