import logging
import json

from flask import render_template
from flask_login import current_user

from editor.utils.formatCharacter import buildChar

from editor.models.storyChars import StoryCharsService, StoryWithCharactersService
from editor.models.chars import CharService
from editor.models.chapters import ChapterService, ChapterCharService

def buildHistory(chat, story, posts, chapter=None):

    logging.debug(f"Building History for Story {story.title}")

    if story.book:
        intro = buildBaseChapter(story, chapter)
    else:
        intro = buildBase(story)

    chat.add_history("user", intro)

    for post in posts:
        logging.debug(f"Processing post: {post.post_id}")
        # Tidy up outstanding messages if building multi-modal message
        if post.source == "post":
            chat.add_history(post.creator, post.content)
            creator = post.creator
        if post.source == "part" and post.part_type == "text":
            chat.add_history(creator, post.part_text)
        if post.source == "part" and post.part_type == "image":
            chat.add_history(
                creator,
                f"Use the following text to describe the character's physical appearance: { post.part_image_description }"
            )

def buildPrompt(content, chars):
    multi_modal_content = []
    multi_modal_content.append({"text": content})
    for ix in chars:
        logging.debug(f"Building prompt for char {ix}")
        char = CharService.get_character(ix, current_user.id)
        txtprompt = buildChar(
            char.name, char.description, char.personality, char.motivation, char.image_mime_type
        )
  
        multi_modal_content.append({"text": txtprompt})
        if char.image_mime_type:

            multi_modal_content.append(
                {
                    "text": f"Use the following text to describe the character's physical appearance: { char.image_description }"
                }
            )

    return multi_modal_content

def buildBase(story):
    logging.debug("Building Base")
    story_chars=StoryWithCharactersService.get_story_with_characters(story.story_id)

    ret_string = render_template("prompts/basePrompt.txt", story=story, characters=story_chars)
    logging.debug(f"Base Prompt: {ret_string}")
    return json.loads(ret_string)

def buildBaseChapter(story, chapter):
    summaries=ChapterService.get_previous_chapters(story.story_id, chapter.position)
    story_chars=[]
    chapter_chars=ChapterCharService.get_chapter_chars(story.story_id, chapter.chapter_id)
    for chapter_char in chapter_chars:
        char=CharService.get_character(chapter_char.char_id, current_user.id)
        if chapter_char.override:
            note=chapter_char.note
        else:
            base_note=StoryCharsService.get_story_chars_base(story.story_id,chapter_char.char_id)
            note=base_note.note

        story_chars.append({
            "name" : char.name,
            "description" : char.description,
            "personality" : char.personality,
            "motivation": char.motivation,
            "image_mime_type" : char.image_mime_type,
            "image_data": char.image_data,
            "image_description": char.image_description,
            "note": note
        })
    ret_string = render_template("prompts/baseChapterPrompt.txt", story=story, chapter=chapter, summaries=summaries, characters=story_chars)
    logging.debug(f"Base Chapter Prompt: {ret_string}")
    return json.loads(ret_string)
