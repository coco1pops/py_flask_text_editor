import json
import logging

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    send_file,
    flash,
    get_flashed_messages
)
from flask_login import current_user

from editor.models.chat_service import get_chat_service

import editor.utils.db
import editor.utils.docwriter

bp = Blueprint("stories", __name__)


@bp.before_request
def require_login():
    if not current_user.is_authenticated:
        logging.debug("Not authenticated")
        return redirect(url_for("login.login"))  # Redirect to your login route


#
# Creates a new story and adds a system instruction record
#
@bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        logging.debug("Creating story ")
        story = request.form["title"]
        note = request.form["note"] or ""
        systeminstruction = request.form["systeminstruction"] or ""

        if story:
            story_id = editor.utils.db.insert_story(story, note, systeminstruction)
            return redirect(url_for("stories.generate_story", story_id=story_id))

    sysints = editor.utils.db.get_sysints()
    return render_template("stories/create.html", sysints=sysints)


# Returns a list of stories
@bp.route("/stories", methods=["GET", "POST"])
def stories():
    if request.method == "POST":
        story_id = request.form.get("action")
        return redirect(url_for("stories.generate_story", story_id=story_id))

    stories = editor.utils.db.get_stories()

    return render_template("stories/stories.html", stories=stories)


#
# Deletes a story and related posts
#
@bp.route("/delete_story", methods=["POST"])
def delete_story():
    story_id = request.values.get("story_id")
    logging.debug(f"Requested delete of row {story_id}")
    if story_id:
        editor.utils.db.delete_story(story_id)
        flash("Story deleted", "success")
        messages = get_flashed_messages(with_categories=True)
        return jsonify({"success": "Record deleted","messages": messages}),200

    return jsonify({"error": "Database delete failed"}), 406


#
# Updates an individual story
#
@bp.route("/update_story", methods=["POST"])
def update_story():
    story_id = request.values.get("story_id")
    field = request.values.get("field")
    value = request.values.get("new value")

    logging.debug(f"Updating {story_id} {field} {value}")
    if story_id:
        editor.utils.db.update_story(story_id, field, value)
        return jsonify({"success": "Record udpdated"}), 200
    return jsonify({"error": "Database update failed"}), 406


#
# Prints a individual story
#
@bp.route("/print_story", methods=["POST"])
def print_story():
    story_id = request.values.get("story_id")
    story = editor.utils.db.get_story(story_id)
    dl_name = f"{story['title']}.docx"
    logging.debug(f"Printing {dl_name}")
    if story_id:
        try:
            doc_buffer = editor.utils.docwriter.generate_doc_from_posts(story_id)
            return send_file(
                doc_buffer,
                as_attachment=True,
                download_name=dl_name,
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        except Exception as e:
            logging.debug(f"Error {e}")
            return jsonify({"error": "Print generation failed"}), 406
    return jsonify({"error": "Missing story id"}), 406


#
# Used to display an individual story and the chat. Behind the scenes it also populates the chat with previous messages
#
@bp.route("/generate_story")
def generate_story():
    story_id = request.values.get("story_id")

    story = editor.utils.db.get_story(story_id)
    posts = editor.utils.db.get_all_posts(story_id)
    chars = editor.utils.db.get_characters()

    return render_template(
        "stories/generate_story.html", story=story, posts=posts, chars=chars
    )


@bp.route("/get_message", methods=["GET"])
def get_message():
    post_id = request.values.get("post_id")

    logging.debug(f"Retrieving message for {post_id}")
    if post_id:
        message = editor.utils.db.get_message(post_id)
        return jsonify({"message": message}), 200
    return jsonify({"error": "Database read failed"}), 406


#
# Assigns a character to a story
#
@bp.route("/assignChar", methods=["POST"])
def assignChar():
    char_id = request.form["char_id"]
    resp = editor.utils.db.build_char(char_id)
    return jsonify(resp), 200

#
# Deletes posts
#
@bp.route("/deleteRows", methods=["POST"])
def deleteRows():
    post_id = request.values.get("post_id")
    story_id = request.values.get("story_id")
    logging.debug(f"Deleting older posts from {post_id}")
    editor.utils.db.delete_posts_from(story_id, post_id)
    flash("Posts deleted", "success")
    messages = get_flashed_messages(with_categories=True)
    return jsonify({"messages": messages}),200

#
# Generates a chat line from a prompt and inserts the response into the database
#
@bp.route("/generate", methods=["POST"])
def generate_text():
    story_id = request.values.get("story_id")
    prompt = request.values.get("prompt")
    mode = request.values.get("mode")
    row_id = request.values.get("row_id")
    chars = json.loads(request.values.get("chars", []))

    if not prompt:
        return (jsonify({"error": "Invalid input. Please provide a JSON object with a 'prompt' key."}),400)

    logging.debug(f"Received prompt: {prompt[:30]}, Mode {mode} Row {row_id} {chars} ")
    #
    # If Edit then all you need to do is update the database
    #
    if mode == "Edit Response":
        success = editor.utils.db.update_message(row_id, prompt)
        if success:
            rows = editor.utils.db.get_post(row_id)
            flash("Response updated", "success")
            messages = get_flashed_messages(with_categories=True)
            return jsonify({"success": "Response update succeeded", "posts" : rows, "messages" : messages}), 200
        else:
            return jsonify({"error": "Response update failed"}), 406

    #
    # If editing prompt need to delete everything after the prompt
    #
    if mode == "Edit Prompt":
        logging.debug(f"Deleting older posts from {row_id}")
        editor.utils.db.delete_posts_from(story_id, row_id)

    # Try to generate more chat
    # Build the chat service
    chat = get_chat_service()
    story = editor.utils.db.get_story(story_id)
    chat.reset_chat(story["systeminstruction"])
    buildHistory(chat, story_id)
    #
    # Generating new content
    #
    try:
        if len(chars) == 0:
            parsed_prompt = prompt
            logging.debug(f"Trying to send prompt {prompt[:30]}")
        else:
            parsed_prompt = buildPrompt(prompt, chars)
            logging.debug("Trying to send multiprompt")
        # Generate content
        # prompt here could be just a message or a multimodal structure
        message = chat.send_message(parsed_prompt)

    except Exception as e:
    #
    # Exception will be logged in the chat class 
    # Field the message here and pass up the chain
    #
        logging.debug("Caught Error")
        if isinstance(e,str):
                mess=e
        else:
                mess=e.args[0]
        logging.debug(f"Error message {mess}")

        flash(f"{mess}", "error")
        messages = get_flashed_messages(with_categories=True)
        return jsonify({"error": "Generation Failed", "messages": messages}), 422
    #
    # Storing prompt and responses
    #
    
    try:
        #
        # Insert new prompt
        #
        if len(chars) > 0:
            multi = True
        else:
            multi = False

        logging.debug("Inserting new prompt into database")

        post_id = editor.utils.db.insert_post(story_id, "user", prompt, multi)

        for ix in chars:
            part = editor.utils.db.get_character_raw(ix)
            text_part = buildChar(
                part["name"],
                part["description"],
                part["personality"],
                part["motivation"],
            )
            editor.utils.db.insert_post_text_part(story_id, post_id, text_part)
            if part["image_mime_type"] != "":
                editor.utils.db.insert_post_image_part(
                    story_id, post_id, part["image_data"], part["image_mime_type"]
                )
        #
        # Insert new message
        #
        posts = editor.utils.db.get_post(post_id)

        newpost_id = editor.utils.db.insert_post(story_id, "model", message, False)
        newpost=editor.utils.db.get_post(newpost_id)
        posts.append(newpost[0])

        flashMessage="New response added"
        if mode == "Edit Prompt":
            flashMessage = "Prompt updated and new response added"

        flash(flashMessage, "success")
        messages = get_flashed_messages(with_categories=True)

        return jsonify({"success": "New Response Added", "posts" : posts, "messages" : messages}), 200
    except:
        logging.error(f"Error storing content: {e}")
        logging.error("Exception Type:", type(e).__name__)
        logging.error("Exception Message:", str(e))

        return jsonify({"error": str(e)}), 500


def buildHistory(chat, story_id):
    multimodal = False
    multimessage = []
    posts = editor.utils.db.get_all_posts_raw(story_id)
    for post in posts:
        # Tidy up outstanding messages if building multi-modal message
        if post["source"] == "post" and multimodal:
            chat.add_history("user", post["content"])
            multimodal = False
            multimessage = []
        # For parts simply add to multimessage
        if post["source"] == "part":
            if post["part_type"] == "text":
                multimessage.append({"text": post["part_text"]})
            elif post["part_type"] == "image":
                multimessage.append(
                    {
                        "inline_data": {
                            "mime_type": post["part_image_mime_type"],
                            "data": post["part_image_data"],
                        }
                    }
                )
        else:  # Getting here we have a post
            if post["multi_modal"]:  # Create a new multimessage
                multimodal = True
                multimessage = []
                multimessage.append({"text": post["content"]})
            else:
                chat.add_history(post["creator"], post["content"])  # Normal post

    if multimodal:
        chat.add_history("user", multimessage)


def buildPrompt(content, chars):
    multi_modal_content = []
    multi_modal_content.append({"text": content})
    for ix in chars:
        char = editor.utils.db.get_character_raw(ix)
        txtprompt = buildChar(
            char["name"], char["description"], char["personality"], char["motivation"]
        )

        multi_modal_content.append({"text": txtprompt})
        if char["image_mime_type"]:
            multi_modal_content.append(
                {
                    "inline_data": {
                        "mime_type": char["image_mime_type"],
                        "data": char["image_data"],
                    }
                }
            )

    return multi_modal_content


def buildChar(name, description, personality, motivation):
    resp = f"This picture shows **{name}**\n\n"

    if description != "":
        resp = f"{resp}**Description:** {description}\n\n"

    if personality != "":
        resp = f"{resp}**Personality:** {personality}\n\n"

    if motivation != "":
        resp = f"{resp}**Motivation:** {motivation}\n\n"

    return resp
