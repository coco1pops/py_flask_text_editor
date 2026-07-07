import json
import logging
import base64
import markdown

from flask import (
    Blueprint,
    request,
    jsonify,
    flash,
    render_template,
    get_flashed_messages,
    url_for,
    redirect,
    abort
)
from flask_login import current_user

from editor.models.chat_service import get_chat_service, ChatResult
from editor.models.stories import StoryService
from editor.models.storyChars import StoryCharsService, StoryWithCharactersService
from editor.models.posts import PostPartService, PostService, UnifiedPostTimelineService 
from editor.models.chapters import ChapterService, ChapterCharService
from editor.models.chars import CharService
from editor.models.params import ModelsService

from editor.utils.formatCharacter import buildChar
from editor.utils.genBuildPrompts import buildBase, buildBaseChapter, buildPrompt, buildHistory

bp = Blueprint("storyGenerate", __name__)
@bp.before_request
def require_login():
    if not current_user.is_authenticated:
        logging.debug("Not authenticated")      
        return redirect(url_for("login.login"))  # Redirect to your login route
#
# Used to display an individual story and the chat. Behind the scenes it also populates the chat with previous messages
#
@bp.route("/generate_story")
def generate_story():
    # Build story info
    story_id = int(request.values.get("story_id"))
    story = StoryService.get_user_story(story_id, current_user.id)
    if not story:
        logging.error(f"Error occurred while fetching story")
        abort(404, description="Story not found or access denied.")

    if story.book:
        chapter_id = int(request.values.get("chapter_id"))
        chapter = ChapterService.get_chapter(chapter_id)
        chars = CharService.get_characters_outside_chapter(story_id, chapter_id, current_user.id)
    else:
        chapter=None
        chars = CharService.get_characters_outside_story(story_id, current_user.id)

    sCOutput=[]
    storyChars = StoryWithCharactersService.get_story_with_characters(story_id)
    for storyChar in storyChars:
        if story.book:
            inChapter=ChapterCharService.get_chapter_chars_by_char(story_id, chapter_id, storyChar.char_id)
            if inChapter:
                if inChapter.override:
                    note=inChapter.note
                else:
                    note=storyChar.note
                formattedStoryChar = formatStoryChar(storyChar, note)
                sCOutput.append(formattedStoryChar)
        else:
            note=storyChar.note
            formattedStoryChar = formatStoryChar(storyChar, note)
            sCOutput.append(formattedStoryChar)
    
    if story.book:
        chapter_id = int(request.values.get("chapter_id"))
        posts = UnifiedPostTimelineService.get_all_posts(story_id, chapter_id=chapter_id)
    else:
        posts = UnifiedPostTimelineService.get_all_posts(story_id)

    formatted_posts=""
    for ix, post in enumerate(posts):
        is_last = (ix == len(posts) - 1)
        formatted_post = render_template("stories/storyAddNewRowStub.html", post=post, is_last=is_last)
        formatted_posts += formatted_post

    models=ModelsService.get_active_models()
    return render_template(
        "stories/storyGenerate.html", story=story, chapter=chapter, posts=formatted_posts, chars=chars, storyChars=sCOutput, models=models, isadmin=current_user.is_admin
    )

def formatStoryChar(storyChar, note):
    textPart=buildChar(storyChar.name, storyChar.description, storyChar.personality, storyChar.motivation, storyChar.image_mime_type, note)
    textPartHTML=markdown.markdown(textPart)
    imagePart=None
    if storyChar.image_mime_type:
        imagePart="data:" + storyChar.image_mime_type + ";base64," + base64.b64encode(storyChar.image_data).decode('utf-8') 
    
    return({"textBundle" : textPartHTML, "image_data": imagePart})

#
# Assigns a character to a story
#
@bp.route("/assignChar", methods=["POST"])
def assignChar():
    char_id = int(request.form["char_id"])
    char = CharService.get_character(char_id, current_user.id)
    if not char:
        logging.error(f"Error occurred while fetching character")
        return jsonify({"success": False, "message": "Character not found or access denied"}), 404
    resp = CharService.build_char(char_id, current_user.id)
    html = render_template("stories/storyAddCharStub.html",id=char_id, image_mime_type=char.image_mime_type, image_data=char.image_data, text=resp['text'])
    return jsonify({"success": True, "message": "Character assigned successfully", "details": resp, "html": html}), 200

#
# Deletes posts
#
@bp.route("/deleteRows", methods=["POST"])
def deleteRows():
    
    post_id = int(request.values.get("post_id"))
    logging.debug(f"Deleting older posts from {post_id}")
    
    story_id = int(request.values.get("story_id"))
    story = StoryService.get_user_story(story_id, current_user.id)
    if not story:
        logging.error(f"Error occurred while fetching story")
        return jsonify({"success": False, "message": "Story not found or access denied"}), 404
    
    if story.book:
        chapter_id= int(request.values.get("chapter_id"))
        try:
            PostService.delete_posts_from(story_id, current_user.id, post_id, chapter_id=chapter_id)
        except Exception as e:
            logging.debug(f"Error deleting posts {e}")
            return jsonify({"success": False, "message": "Database delete failed"}), 406
    else:
        try:
            PostService.delete_posts_from(story_id, current_user.id, post_id)
        except Exception as e:
            logging.debug(f"Error deleting posts {e}")
            return jsonify({"success": False, "message": "Database delete failed"}), 406
        
    flash("Posts deleted", "success")
    messages = get_flashed_messages(with_categories=True)
    return jsonify({"success": True, "message": "Posts deleted successfully", "messages": messages}), 200

@bp.route("/addButtons", methods=["POST"])
def addButtons():
    post_id = int(request.values.get("post_id"))
    logging.debug(f"Adding buttons for {post_id}")
    if post_id:
        html = render_template("stories/storyAddButtonsStub.html", post_id=post_id, creator="model")
        return jsonify({"success": True, "message": "Buttons added successfully", "html": html}), 200
    
    return jsonify({"success": False, "message": "Generating buttons failed"}), 406

#
# Generates a chat line from a prompt and inserts the response into the database
#
@bp.route("/generate", methods=["POST"])
def generate_text():

    data = parse_generate_request()

    if not data['prompt']:
        return (jsonify({"success": False, "message": "Invalid input. Please provide a JSON object with a 'prompt' key."}),400)

    logging.debug(f"Received prompt: {data['prompt'][:30]}, Mode {data['mode']} Row {data['row_id']} {data['chars']} ")
    #
    # First get the story
    #
    story=StoryService.get_user_story(data['story_id'], current_user.id)
    if not story:
        logging.error(f"Error occurred while fetching story")
        return jsonify({"success": False, "message": "Story not found or access denied"}), 404
    #
    # If Edit then all you need to do is update the database
    #
    if data['mode'] == "Edit Response":
        return handle_edit_response(data['row_id'], data['prompt'])
    #
    # If editing prompt need to delete everything after the prompt
    #
    # Generating chat can return an error in which case we don't want to delete the posts; however we need 
    # to make sure they don't get added to the chat_history before generation. Set a limit to the row_id of the prompt being 
    # edited so that only posts before that are added to the chat history.   
    # 
    limit=None
    if data['mode'] == "Edit Prompt":
        limit=data['row_id']

    # Try to generate more chat

    chatresult=ChatResult(False,None, "","")

    try:
        if story.book:
            chatresult = generate_chat_message(data['story_id'], data['prompt'], data['chars'], chapter_id=data['chapter_id'], limit=limit)
        else:
            chatresult = generate_chat_message(data['story_id'], data['prompt'], data['chars'], limit=limit)

        if chatresult.success:
            message=chatresult.text
        else:
            mess= f"Error: {chatresult.text}, Reason: {chatresult.finish_reason}, Info: {chatresult.safety_ratings}"
            return json_response(
            {"success": False, "message": "Generation Failed"},
            422,
            flash_msg=mess,
            category="error"
        )

    except Exception as e:
        logging.error(f"Could not generate response {e}")
        
        mess="Problem Processing Prompt"

        return json_response(
            {"success": False, "message": "Generation Failed"},
            500,
            flash_msg=mess,
            category="error"
        )
    #
    # Storing prompt and responses
    #
    try:
        if data['mode'] == "Edit Prompt":
            delete_posts(data['story_id'], limit, chapter_id=data['chapter_id'] if story.book else None)
        
        posts, flash_msg = save_prompt_and_response(
            data["story_id"],
            data["chapter_id"],
            data["prompt"],
            data["chars"],
            message,
            data["mode"]
        )

        return json_response(
            {"success": True, "message": "New Response Added", "posts": posts},
            200,
            flash_msg=flash_msg
        )

    except Exception as e:
        logging.exception("Error storing content")
        return jsonify({"success": False, "message": str(e)}), 500

def parse_generate_request():
    chapter_id_raw = request.values.get("chapter_id")
    chapter_id = int(chapter_id_raw) if chapter_id_raw else None
    return {
        "story_id": int(request.values.get("story_id")),
        "chapter_id" : chapter_id,
        "prompt": request.values.get("prompt"),
        "mode": request.values.get("mode"),
        "row_id": int(request.values.get("row_id")),
        "chars": json.loads(request.values.get("chars", "[]")),
    }
def delete_posts(story_id, row_id, chapter_id=None):
    try:
        if chapter_id:
            logging.debug(f"Deleting newer posts from {row_id} for story {story_id} chapter {chapter_id}")
            PostService.delete_posts_from(story_id, current_user.id ,row_id, chapter_id=chapter_id)
        else:
            logging.debug(f"Deleting newer posts from {row_id} for story {story_id}")
            PostService.delete_posts_from(story_id, current_user.id, row_id)
        return
    except Exception as e:
        logging.debug(f"Error deleting posts {e}")
        raise Exception("Posts delete failed")
#
# Utility function to return a consistent json response with any flash messages included. 
# Can be used for any endpoint that needs to return a json response and also include flash messages.
#
def json_response(payload, status=200, flash_msg=None, category="success"):
    if flash_msg:
        flash(flash_msg, category)
    messages = get_flashed_messages(with_categories=True)
    payload["messages"] = messages
    return jsonify(payload), status

def handle_edit_response(row_id, prompt):
    logging.debug("Handling edit response")
    success = PostService.update_message(row_id, prompt, current_user.id)

    if not success:
        return json_response({"success": False, "message": "Response update failed"}, 406)

    posts = UnifiedPostTimelineService.get_post(row_id)
    return json_response(
        {"success": True, "message": "Response update succeeded", "posts": posts},
        flash_msg="Response updated"
    )

def generate_chat_message(story_id, prompt, chars, chapter_id=None, limit=None):
    chat = get_chat_service()
    story = StoryService.get_user_story(story_id, current_user.id)
    if chapter_id:
        chapter = ChapterService.get_chapter(chapter_id)
    else:
        chapter = None


    chat.reset_chat(story)
    #
    # The first prompt needs to be built as a combination of the base and the new prompt
    #
    posts=UnifiedPostTimelineService.get_all_posts_raw(story_id, chapter_id=chapter_id, limit=limit)

    parsed_prompt = prompt if not chars else buildPrompt(prompt, chars)
    buildHistory(chat, story, posts, chapter=chapter)

    return chat.send_message(parsed_prompt)

def save_prompt_and_response(story_id, chapter_id, prompt, chars, message, mode):
    multi = len(chars) > 0

    # multi determines if there are parts to add to the post. Add the post first
    # indicating whether there are further parts
  
    post_id = PostService.insert_post(story_id, current_user.id, "user", prompt, multi, chapter_id=chapter_id)

    # Add a character as a part for each character

    for ix in chars:
        part = CharService.get_character(ix, current_user.id)

        text_part = buildChar(
            part.name,
            part.description,
            part.personality,
            part.motivation,
            part.image_mime_type
        )

        PostPartService.insert_post_text_part(story_id, current_user.id, post_id, text_part, chapter_id=chapter_id)
        # If there is an image associated with the character, add a part
          
        if part.image_mime_type:
            PostPartService.insert_post_image_part(
                story_id, post_id, part.image_data, part.image_mime_type, part.image_description, chapter_id=chapter_id
            )

    posts = UnifiedPostTimelineService.get_post(post_id)

    # Now add the response as a new post

    newpost_id = PostService.insert_post(story_id, current_user.id, "model", message, False, chapter_id=chapter_id)
    newpost = UnifiedPostTimelineService.get_post(newpost_id)

    # Send back the new post as part of the response so it can be added to the screen.
    posts.append(newpost[0])

    flash_msg = (
        "Prompt updated and new response added"
        if mode == "Edit Prompt"
        else "New response added"
    )

    formatted_posts=""
    for ix, post in enumerate(posts):
        is_last = (ix == len(posts) - 1)
        formatted_post = render_template("stories/storyAddNewRowStub.html", post=post, is_last=is_last)
        formatted_posts += formatted_post

    return formatted_posts, flash_msg