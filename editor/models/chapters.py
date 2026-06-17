from editor.models.database import db, print_except
from editor.models.stories import StoryService
from flask_login import current_user

from datetime import datetime

import logging
import markdown

class Chapter(db.Model):
    __tablename__ = "chapters"

    chapter_id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.story_id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    position = db.Column(db.Integer, nullable=False)
    introduction = db.Column(db.Text, nullable=True)
    goal=db.Column(db.Text, nullable=True)
    summary=db.Column(db.Text, nullable=True)
    memory=db.Column(db.Text, nullable=True)
    status=db.Column(db.String(20), nullable=False, default="in_progress")
    chapter_chars = db.relationship(
        'ChapterChar',
        backref='chapter',
        cascade='all, delete-orphan'
    )

class ChapterChar(db.Model):
    __tablename__ = "chapter_chars"
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer,nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=False)
    char_id = db.Column(db.Integer, db.ForeignKey('chars.char_id'), nullable=False)
    override = db.Column(db.Boolean, default=False)
    note =  db.Column(db.Text, nullable=True)

class ChapterService:
    @staticmethod
    def get_chapter(chapter_id, allow_not_found=False):
        try:
            chapter = db.session.get(Chapter, chapter_id)
            if not chapter and not allow_not_found:
                print_except("get_chapter", "Record not found")
            return chapter
        except Exception as e:
            print_except("get_chapter", e)
    
    @staticmethod
    def get_chapter_for_display(chapter_id):
        try:
            chapter = db.session.get(Chapter, chapter_id)
            if not chapter:
                print_except("get_chapter", "Record not found")
            return {"story_id" : chapter.story_id,
                    "chapter_id" : chapter.chapter_id,
                    "title" : chapter.title,
                    "created" : chapter.created,
                    "position" : chapter.position,
                    "introduction" : chapter.introduction,
                    "goal" : chapter.goal,
                    "summary" : chapter.summary,
                    "disp_summary" : markdown.markdown(chapter.summary),
                    "memory" : chapter.memory,
                    "status" : chapter.status}
        except Exception as e:
            print_except("get_chapter_for_display", e)

    @staticmethod
    def get_chapters(story_id):
        try:
            chapters = Chapter.query.filter_by(story_id=story_id).order_by(Chapter.position.asc()).all()
            return chapters

        except Exception as e:
            print_except("get_chapters", e)

    @staticmethod
    def get_next_chapter_position(story_id):
        try:
            chapter = Chapter.query.filter_by(story_id=story_id).order_by(Chapter.position.desc()).first()
            if chapter:
                return (chapter.position+1)
            else:
                return 1

        except Exception as e:
            print_except("get_next_chapter_position", e)
    
    @staticmethod
    def get_previous_chapter_summary(story_id, position):
        try:
            chapter = (Chapter.query.filter(Chapter.story_id==story_id, 
                Chapter.position < position
                )
                .order_by(Chapter.position.desc())
                .first()
            )
            if chapter:
                return chapter.summary
            else:
                return None

        except Exception as e:
            print_except("get_previous_chapter_summary", e)

    @staticmethod
    def get_previous_chapters(story_id, position):
        try:
            chapters = (Chapter.query.filter(Chapter.story_id==story_id, 
                Chapter.position < position
                )
                .order_by(Chapter.position.asc())
                .all()
            )
            return chapters

        except Exception as e:
            print_except("get_previous_chapters", e)

    @staticmethod
    def get_chapter_by_position(story_id, position):
        try:
            chapter = (Chapter.query.filter(Chapter.story_id==story_id, 
                Chapter.position==position
                )
                .order_by(Chapter.position.asc())
                .first()
            )
            return chapter

        except Exception as e:
            print_except("get_previous_chapters", e)

    @classmethod
    def update_chapter(cls, chapter_id, field, value):
        try:
            chapter = cls.get_chapter(chapter_id)
            if not chapter:
                return False
            StoryService.touch_story(chapter.story_id, current_user.id)
            setattr(chapter, field, value)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print_except("update_chapter",e)
    
    @classmethod
    def update_chapter_all(cls, chapter_id, title, position, introduction, goal, memory):
        try:
            chapter = cls.get_chapter(chapter_id)
            if not chapter:
                return False
            StoryService.touch_story(chapter.story_id, current_user.id)
            chapter.title=title
            chapter.position=position
            chapter.introduction=introduction
            chapter.goal=goal
            chapter.memory=memory
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print_except("update_chapter",e)
          
    @staticmethod
    def insert_chapter(story_id, title, position, introduction, goal, memory):
        try:            
            chapter = Chapter(
                story_id=story_id,
                title=title,
                position=position,
                introduction=introduction,
                goal=goal,
                summary="",
                memory=memory
            )
            db.session.add(chapter)
            StoryService.touch_story(story_id, current_user.id)
            db.session.commit()
            return chapter.chapter_id
        
        except Exception as e:
            db.session.rollback()
            print_except("insert_post",e)   

    @classmethod
    def delete_chapter(cls, chapter_id):
        try:
            chapter = cls.get_chapter(chapter_id)

            if not chapter:
                return False

            db.session.delete(chapter)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print_except("delete_chapter", e)

class ChapterCharService:

    @staticmethod
    def get_chapter_char(id, allow_not_found=False):
        try:
            chapter_char = db.session.get(ChapterChar, id)
            if not chapter_char and not allow_not_found:
                print_except("get_chapter_char", "Record not found")
            return chapter_char
        except Exception as e:
            print_except("get_chapter_char", e)

    @staticmethod
    def get_chapter_chars(story_id, chapter_id):
        try:
            return ChapterChar.query.filter_by(story_id=story_id, chapter_id=chapter_id).all()
        except Exception as e:
            print_except("get_chapter_chars", e)

    @staticmethod
    def get_chapter_chars_by_char(story_id, chapter_id, char_id):
        try:
            return ChapterChar.query.filter_by(story_id=story_id, chapter_id=chapter_id, char_id=char_id).first()
        except Exception as e:
            print_except("get_chapter_chars_by_char", e)

    @staticmethod
    def delete_chapter_chars_by_story(story_id, char_id):
        try:
            return ChapterChar.query.filter_by(story_id=story_id, char_id=char_id).delete(synchronize_session=False)

        except Exception as e:
            print_except("delete_chapter_chars_by_story", e)

    @staticmethod
    def insert_chapter_char(story_id, chapter_id, char_id, note):
        try:
            chapter_char=ChapterChar(story_id=story_id, chapter_id=chapter_id, char_id=char_id, note=note)
            db.session.add(chapter_char)
            StoryService.touch_story(story_id, current_user.id)
            db.session.commit()
            return chapter_char.id
        
        except Exception as e:
            print_except("insert_chapter_char", e)
    
    @classmethod
    def update_chapter_char(cls, id, field, value):
        chapter_char=cls.get_chapter_char(id)
        if not chapter_char:
            return False        
        try:
            setattr(chapter_char, field, value)
            db.session.commit()
        except Exception as e:
            print_except("update_chapter_char", e)

    @classmethod
    def delete_chapter_char(cls, id):
        chapter_char=cls.get_chapter_char(id)
        if not chapter_char:
            print_except("delete_chapter_char", "Record not found")     
        try:
            db.session.delete(chapter_char)
            db.session.commit()
        except Exception as e:
            print_except("delete_chapter_char", e)

    @staticmethod
    def get_assigned_char_subquery(story_id, chapter_id):

        return db.session.query(ChapterChar.char_id)\
            .filter_by(story_id=story_id, chapter_id=chapter_id)