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

from editor.models.stories import Story, StoryService
from editor.models.storyChars import StoryWithCharactersService
from editor.models.chars import CharService
from editor.models.params import ParamsService
from editor.models.sysints import SysIntService

import editor.utils.docwriter

bp = Blueprint("stories", __name__)

@bp.before_request
def require_login():
    if not current_user.is_authenticated:
        logging.debug("Not authenticated")
        return redirect(url_for("login.login"))  # Redirect to your login route


#
# Creates a new story and adds the various parameters for the chat
#
@bp.route("/create", methods=["GET", "POST"])
@bp.route("/create/<int:story_id>", methods=["GET", "POST"])
def create(story_id=None):

    mode= "Edit" if story_id else "Create"
    params = ParamsService.get_params(1)
    if not params:
        raise Exception("No parameters found. Please ensure there is a record in the params table with id 1")

    if request.method == "POST":
        but = request.form.get("action")
        if but == "Generate":
            return redirect(url_for("storyGenerate.generate_story", story_id=story_id))
        elif but == "Chapters":
            return redirect(url_for("chapters.chapters", story_id=story_id))

        if mode == "Edit":
            logging.debug(f"Updating story {story_id}")
            story = StoryService.get_story(story_id)
            storyChars = StoryWithCharactersService.get_story_with_characters(story_id)
        else:
            book = "book" in request.form
            logging.debug("Creating story ")
        
        title = request.form["title"]
        note = request.form["note"] or ""
        systeminstruction = request.form["systeminstruction"] or ""
        world_rules = request.form["world_rules"] or ""
        paramsUpdated = request.form.get("paramsSaved") == "True"

        if (paramsUpdated and mode == "Create") or mode=="Edit":
            logging.debug("Getting Studio Details")
            temperature=request.form.get('studio_temperature')
            top_p=request.form.get('studio_top_p')
            harassment_threshold=request.form.get('studio_harassment_threshold')
            hate_speech_threshold=request.form.get('studio_hate_speech_threshold')
            dangerous_content_threshold=request.form.get('studio_dangerous_content_threshold')
            explicit_content_threshold=request.form.get('studio_explicit_content_threshold')
            model=request.form.get('studio_model')
 
        elif mode == "Create":
            temperature=params.temperature
            top_p=params.top_p
            harassment_threshold=params.harassment_threshold
            hate_speech_threshold=params.hate_speech_threshold
            dangerous_content_threshold=params.dangerous_content_threshold
            explicit_content_threshold=params.explicit_content_threshold
            model=params.model
            world_rules=params.world_rules

        if mode == "Create":
            story_id =StoryService.insert_story(title, note, systeminstruction, temperature, 
                top_p, harassment_threshold, hate_speech_threshold, dangerous_content_threshold, 
                explicit_content_threshold, model, world_rules, book)
            story=StoryService.get_story(story_id)
            storyChars = []
            flash("Story Added", "success")
        else:
            StoryService.update_story_all(story_id, title, note, systeminstruction, temperature, 
                top_p, harassment_threshold, hate_speech_threshold, dangerous_content_threshold, 
                explicit_content_threshold, model, world_rules)
            flash("Story Updated", "success")
        
        return redirect(url_for("stories.create", story_id=story_id))
    else:
        story = Story(                
            title="",
            note="",
            systeminstruction="",
            book=False,
            temperature=params.temperature or 0.7,
            top_p=params.top_p or 0.9,
            harassment_threshold=params.harassment_threshold,
            hate_speech_threshold=params.hate_speech_threshold,
            dangerous_content_threshold=params.dangerous_content_threshold,
            explicit_content_threshold=params.explicit_content_threshold,
            model=params.model,
            world_rules=params.world_rules
            )
        storyChars = []
        if story_id:
            logging.debug(f"Loading story {story_id}")
            story = StoryService.get_story(story_id)
            storyChars = StoryWithCharactersService.get_story_with_characters(story_id)

    sysints = SysIntService.get_sysints()
    chars = CharService.get_characters()
    return render_template("stories/storyCreate.html", 
        story=story, 
        storyChars=storyChars, 
        sysints=sysints, 
        chars=chars, 
        isadmin=current_user.is_admin)

# Returns a list of stories
@bp.route("/stories", methods=["GET", "POST"])
def stories():
    if request.method == "POST":
        action = request.form.get("action")
        
        if action.startswith("Generate:"):
            story_id = action.split(":")[1]
            story=StoryService.get_story(story_id)
            if story.book:
                return redirect(url_for("chapters.chapters", story_id=story_id))
            else:
                return redirect(url_for("storyGenerate.generate_story", story_id=story_id))
        else:
            story_id = action
            return redirect(url_for("stories.create", story_id=story_id))

    stories = StoryService.get_stories()

    return render_template("stories/storiesList.html", stories=stories)

#
# Deletes a story and related posts
#
@bp.route("/delete_story", methods=["POST"])
def delete_story():
    story_id = int(request.values.get("story_id"))
    logging.debug(f"Requested delete of row {story_id}")
    if story_id:
        StoryService.delete_story(story_id)
        flash("Story deleted", "success")
        messages = get_flashed_messages(with_categories=True)
        return jsonify({"success": "Record deleted","messages": messages}),200

    return jsonify({"error": "Database delete failed"}), 406


#
# Updates an individual story
#
@bp.route("/update_story", methods=["POST"])
def update_story():
    story_id = int(request.values.get("story_id"))
    field = request.values.get("field")
    value = request.values.get("new value")

    logging.debug(f"Updating {story_id} {field} {value}")
    if story_id:
        StoryService.update_story(story_id, field, value)
        return jsonify({"success": "Record udpdated"}), 200
    return jsonify({"error": "Database update failed"}), 406


#
# Prints a individual story
#
@bp.route("/print_story", methods=["POST"])
def print_story():
    story_id = int(request.values.get("story_id"))
    story = StoryService.get_story(story_id)
    dl_name = f"{story.title}.docx"
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
