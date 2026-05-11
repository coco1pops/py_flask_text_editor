from editor.models.database import db, print_except
from editor.models.stories import StoryService

from datetime import datetime

import base64
import markdown
import logging

class Post(db.Model):
    __tablename__ = "posts"

    post_id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.story_id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    creator = db.Column(db.String(255), nullable=False)
    multi_modal = db.Column(db.Boolean, default=False)
    post_parts = db.relationship(
        'PostPart',
        backref='post',
        cascade='all, delete-orphan'
    )

class UnifiedPostTimeline(db.Model):
    __tablename__ = "unified_post_timeline"

    post_id = db.Column(db.Integer, primary_key=True)
    part_id= db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, nullable=False)
    chapter_id =db.Column(db.Integer, nullable=True)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    creator = db.Column(db.String(255), nullable=False)
    multi_modal = db.Column(db.Boolean, default=False)
    source = db.Column(db.String(50), nullable=False)  # 'post' or 'part'
    part_type = db.Column(db.String(50))  # 'text' or 'image' for parts
    part_text = db.Column(db.Text)  # For text parts
    part_image_data = db.Column(db.LargeBinary)  # For image parts
    part_image_mime_type = db.Column(db.String(255))  # MIME type for image parts

class PostPart(db.Model):
    __tablename__ = "post_parts"

    part_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    story_id = db.Column(db.Integer, nullable=False)
    chapter_id = db.Column(db.Integer, nullable=True)
    part_type = db.Column(db.String(50), nullable=False)  # 'text' or 'image'
    part_text = db.Column(db.Text)  # For text parts
    part_image_data = db.Column(db.LargeBinary)  # For image parts
    part_image_mime_type = db.Column(db.String(255))  # MIME type for image parts
    created = db.Column(db.DateTime, default=datetime.utcnow)


class UnifiedPostTimelineService:
    @classmethod
    def get_post(cls, post_id, allow_not_found=False):
        try:
            posts = UnifiedPostTimeline.query.filter_by(post_id=post_id).all()

            if not posts and not allow_not_found:
                print_except("get_post", "Record not found")

            format_post = cls.parse_timeline(posts)

            return format_post
        except Exception as e:
            print_except("get_post", e)
    
    @staticmethod
    def get_all_posts_raw(story_id, chapter_id=None):
        try:
            if chapter_id:
                return UnifiedPostTimeline.query.filter_by(story_id=story_id, chapter_id=chapter_id).all()
            else:
                return UnifiedPostTimeline.query.filter_by(story_id=story_id).all()
        except Exception as e:
            print_except("get_timeline", e)

    @classmethod
    def get_all_posts(cls, story_id, chapter_id=None):
        try:
            if chapter_id:
                posts = cls.get_all_posts_raw(story_id, chapter_id=chapter_id)
            else:
                posts = cls.get_all_posts_raw(story_id)
            format_posts = cls.parse_timeline(posts)

            return format_posts
        
        except Exception as e:
            print_except("get_all_posts", e)

    @staticmethod
    def parse_timeline(posts): 
        logging.debug(f"Parsing timeline with {len(posts)} posts")
        format_posts = []
        posts_ix = 0
        for post in posts:
            message = ""
            upd = False
            if post.source =="post":
                message =  markdown.markdown(post.content)
                content = post.content
            if post.source == 'part' and post.part_type =='text':
                message =  markdown.markdown(post.part_text)
                content = post.part_text
            if post.source == 'part' and post.part_type == 'image' and post.part_image_mime_type:
                image_data ="data:" + post.part_image_mime_type + ";base64," + base64.b64encode(post.part_image_data).decode('utf-8')
                upd=True
            else:
                image_data = ''
            
            if upd:
                format_posts[posts_ix - 1]['image_data'] = image_data
                format_posts[posts_ix - 1]['image_mime_type'] = post.part_image_mime_type
            else:
                format_posts.append({'post_id' : post.post_id, 
                                    'created' : post.created, 
                                    'creator' : post.creator,
                                    "multi_modal" : post.multi_modal, 
                                    "source" : post.source, 
                                    "part_type": post.part_type, 
                                    "message" : message, 
                                    "message_md" : content, 
                                    'image_data' : image_data, 
                                    "image_mime_type" : post.part_image_mime_type})
            
                posts_ix += 1
            logging.debug(f"Parsed post {post.post_id} from source {post.source} with part type {post.part_type}")

        return format_posts


class PostService:
    @staticmethod
    def get_message(post_id, allow_not_found=False):
        try:
            post = db.session.get(Post, post_id)
            if not post and not allow_not_found:
                print_except("get_message", "Record not found")
            return post
        except Exception as e:
            print_except("get_message", e)

    @staticmethod
    def get_chapter_posts(story_id,chapter_id):
        try:
            return Post.query.filter_by(story_id=story_id, chapter_id=chapter_id).all()
        except Exception as e:
            print_except("get_chapter_posts", e)

    @classmethod
    def update_message(cls,post_id, value):
        try:
            post = cls.get_message(post_id)
            if not post:
                return False
            StoryService.touch_story(post.story_id)
            post.message = value
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print_except("update_message",e)

    @staticmethod
    def delete_posts_from(story_id, post_id, chapter_id=None):
        try:
            if chapter_id:
                db.session.query(PostPart).filter(
                    PostPart.story_id == story_id,
                    PostPart.chapter_id == chapter_id,
                    PostPart.post_id >= post_id
                    ).delete(synchronize_session=False)

                db.session.query(Post).filter(
                    Post.story_id == story_id,
                    Post.chapter_id == chapter_id,
                    Post.post_id >= post_id
                ).delete(synchronize_session=False)
            else:
                db.session.query(PostPart).filter(
                    PostPart.story_id == story_id,
                    PostPart.post_id >= post_id
                    ).delete(synchronize_session=False)

                db.session.query(Post).filter(
                    Post.story_id == story_id,
                    Post.post_id >= post_id
                ).delete(synchronize_session=False)

            StoryService.touch_story(story_id)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print_except("delete_posts_from",e)
          
    @staticmethod
    def insert_post(story_id, creator, prompt, multi, chapter_id=None):
        try:            
            post = Post(
                story_id=story_id,
                chapter_id=chapter_id,
                creator=creator,
                message=prompt,
                multi_modal=multi
            )
            db.session.add(post)
            StoryService.touch_story(story_id)
            db.session.commit()
            return post.post_id
        
        except Exception as e:
            db.session.rollback()
            print_except("insert_post",e)   

class PostPartService:
    @staticmethod
    def insert_post_text_part(story_id, post_id, part_text, chapter_id=None):
        try:
            post_part = PostPart(
                post_id=post_id,
                story_id=story_id,
                chapter_id=chapter_id,
                part_type="text",
                part_text=part_text
            )
            db.session.add(post_part)
            StoryService.touch_story(story_id)
            db.session.commit()
            return post_part.part_id
        except Exception as e:
            db.session.rollback()
            print_except("insert_post_part", e)

    @staticmethod
    def insert_post_image_part(story_id, post_id, image_data, image_mime_type, chapter_id=None):
        try:
            post_part = PostPart(
                post_id=post_id,
                story_id=story_id,
                chapter_id=chapter_id,
                part_type="image",
                part_image_data=image_data,
                part_image_mime_type=image_mime_type
            )
            db.session.add(post_part)
            db.session.commit()
            return post_part.part_id
        except Exception as e:
            db.session.rollback()
            print_except("insert_post_part", e)
    