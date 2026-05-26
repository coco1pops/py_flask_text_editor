import logging
import markdown

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
from flask_login import login_required, current_user

from editor.models.stories import StoryService
from editor.models.chapters import Chapter, ChapterService, ChapterCharService
from editor.models.storyChars import StoryWithCharactersService
from editor.utils.docwriter import generate_doc_from_posts
from editor.models.posts import PostService
from editor.models.chars import CharService

from editor.models.chat_service import get_chat_service

bp = Blueprint("chapters", __name__)

@bp.before_request
def require_login():
    if not current_user.is_authenticated:
        logging.debug("Not authenticated")
        return redirect(url_for("login.login"))  # Redirect to your login route


#
# Creates a new story and adds the various parameters for the chat
#
@bp.route("/story/<int:story_id>/chapter/create", methods=["GET", "POST"])
@bp.route("/story/<int:story_id>/chapter/<int:chapter_id>", methods=["GET", "POST"])
@login_required
def create_chapter(story_id, chapter_id=None):

    #chapter=None
    mode= "Edit" if chapter_id else "Create"
    story = StoryService.get_story(story_id)
    story_chars=None

    if mode == "Edit":
        chapter=ChapterService.get_chapter_for_display(chapter_id)
        story_chars=buildChapterChars(story_id, chapter_id)
    else:
        position=ChapterService.get_next_chapter_position(story_id)
        chapter=Chapter(title="", introduction="", goal="", position=position, memory="")

    if request.method == "POST":        
        
        # Exit out if generate pressed
        but = request.form.get("action")
        if but == "Generate":
            return redirect(url_for("storyGenerate.generate_story", story_id=story_id, chapter_id=chapter_id))
        
        title = request.form["title"]
        position = int(request.form["position"])
        introduction = request.form["introduction"] or ""
        goal = request.form["goal"] or ""
        memory = request.form["memory"] or ""

        err=False 
        if_exists = ChapterService.get_chapter_by_position(story_id, position)
        if if_exists:
            if mode=="Create":
                err=True
                chapter=Chapter(title=title, introduction=introduction, goal=goal, position=position, memory=memory)
            else:
                if if_exists.chapter_id != chapter_id:
                    chapter.title=title
                    chapter.position=position
                    chapter.introduction=introduction
                    chapter.goal=goal
                    chapter.memory=memory
                    err=True    
        if err:    
            flash("Chapter Already Exists in this Position", "danger")
            return render_template("stories/chapterCreate.html", 
                story=story, 
                chapter=chapter,
                story_chars=story_chars)

        if mode=="Edit":
            status=request.form["status"]
            ChapterService.update_chapter_all(chapter_id, title, position, introduction, goal, 
                memory, status)
            flash("Chapter Updated", "success")

        else:
            chapter_id = ChapterService.insert_chapter(story_id, title, position, introduction, goal, memory) 
            chapter=ChapterService.get_chapter_for_display(chapter_id)
            flash("Chapter Added", "success")
        
        return redirect(url_for("chapters.create_chapter", story_id=story_id, chapter_id=chapter_id))

    return render_template("stories/chapterCreate.html", 
        story=story, 
        chapter=chapter,
        story_chars=story_chars)

#
# Updates an individual chapter
#
@bp.route("/update_chapter", methods=["POST"])
def update_chapter():
    story_id = int(request.values.get("story_id"))
    chapter_id=int(request.values.get("chapter_id"))
    field = request.values.get("field")
    value = request.values.get("new value")

    logging.debug(f"Updating Story {story_id}, Chapter {chapter_id} {field} {value}")
    if story_id:
        ChapterService.update_chapter(chapter_id, field, value)
        if field == "summary":
            chapter=ChapterService.get_chapter_for_display(chapter_id)
            return jsonify({"success": True, "message": "Record updated", "disp_summary": chapter["disp_summary"]}), 200
        else:
            return jsonify({"success": True, "message": "Record updated"}), 200
    return jsonify({"success": False, "message": "Database update failed"}), 406


def buildChapterChars(story_id, chapter_id):
    dict=[]
    story_chars=StoryWithCharactersService.get_story_with_characters(story_id)
    for story_char in story_chars:
        id=story_char.id
        char_id=story_char.char_id
        chapter_char_id = None
        name=story_char.name
        description=story_char.description
        notes=story_char.note
        base_notes=story_char.note
        override=False
        involved=False
        chapter_char=ChapterCharService.get_chapter_chars_by_char(story_id, chapter_id, story_char.char_id)
        if chapter_char:
            chapter_char_id = chapter_char.id
            involved=True
            if chapter_char.override:
                override=True
                notes=chapter_char.note
        
        dict.append({"id" : id,
                     "chapter_char_id": chapter_char_id, 
                     "name" : name, 
                     "char_id" : char_id,
                     "description" : description, 
                     "notes" : notes, 
                     "base_notes" : base_notes,
                     "override": override,
                     "involved" : involved})
    
    return dict


# Returns a list of chapters for a story
@bp.route("/story/<int:story_id>/chapters", methods=["GET", "POST"])
@login_required
def chapters(story_id):
    story=StoryService.get_story(story_id)
    if request.method == "POST":
        action = request.form.get("action")
        if action.startswith("Generate:"):
            chapter_id = action.split(":")[1]
            return redirect(url_for("storyGenerate.generate_story", story_id=story_id, chapter_id=chapter_id))
        else:
            chapter_id = action
            return redirect(url_for("chapters.create_chapter", story_id=story_id, chapter_id=chapter_id))

    chapters = ChapterService.get_chapters(story_id)

    return render_template("stories/chapterList.html", story=story, chapters=chapters)

@bp.route("/addChapterCharacter", methods=["POST"])
@login_required
def addChapterCharacter():
    story_id=int(request.values.get("story_id"))
    chapter_id=int(request.values.get("chapter_id"))
    char_id=int(request.values.get("char_id"))
    try:
        row_id = ChapterCharService.insert_chapter_char(story_id, chapter_id, char_id,"")
        return ({"success": True, "row_id": row_id, "message": "Character added to chapter"}), 200
    except Exception as e:
        logging.debug(f"Error {e}")
        return jsonify({"success": False, "message": "Database insert failed"}), 406

@bp.route("/deleteChapterCharacter", methods=["POST"])
@login_required
def deleteChapterCharacter():
    id=request.values.get("id")
    try:
        ChapterCharService.delete_chapter_char(id)
        return ({"success": True, "message": "Character removed from chapter"}), 200
    except Exception as e:
        logging.debug(f"Error {e}")
        return jsonify({"success": False, "message": "Database delete failed"}), 406    

@bp.route("/updateChapterCharacter", methods=["POST"])
@login_required
def updateChapterCharacter():
    id=request.values.get("id")
    field=request.values.get("field")
    value=request.values.get("value")
    if field=="override":
        value= value == "true"
    try:
        ChapterCharService.update_chapter_char(id, field, value)
        return ({"success": True, "message": "Character updated"}), 200
    except Exception as e:
        logging.debug(f"Error {e}")
        return jsonify({"success": False, "message": "Database update failed"}), 406

#
# Deletes a chapter and related posts
#
@bp.route("/delete_chapter", methods=["POST"])
def delete_chapter():
    story_id = int(request.values.get("story_id"))
    chapter_id = int(request.values.get("chapter_id"))
    logging.debug(f"Requested delete of story {story_id}, chapter {chapter_id}")
    if story_id and chapter_id:
        try:
            ChapterService.delete_chapter(chapter_id)
            flash("Chapter deleted", "success")
            messages = get_flashed_messages(with_categories=True)
            return jsonify({"success": True, "messages": messages}),200
        except Exception as e:
            logging.debug(f"Error {e}")
            return jsonify({"success": False, "message": "Database delete failed"}), 406

    return jsonify({"success": False, "message": "Database delete failed"}), 406

#
# Prints an individual chapter
#
@bp.route("/print_chapter", methods=["POST"])
def print_chapter():
    data=request.get_json()
    story_id = int(data.get("story_id"))
    chapter_id = int(data.get("chapter_id"))

    story = StoryService.get_story(story_id)
    chapter=ChapterService.get_chapter(chapter_id)

    dl_name = f"{story.title} {chapter.title}.docx"
    logging.debug(f"Printing {dl_name}")
    if story_id and chapter_id:
        try:
            doc_buffer=generate_doc_from_posts(story_id, chapter_id)
            return send_file(
                doc_buffer,
                as_attachment=True,
                download_name=dl_name,
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        except Exception as e:
            logging.debug(f"Error {e}")
            return jsonify({"success": False, "message": "Document generation failed"}), 406
    return jsonify({"success": False, "message": "Missing story or chapter id"}), 406

@bp.route("/summarise_chapter", methods=["POST"])
def summarise_chapter():
    story_id = int(request.values.get("story_id"))
    chapter_id = int(request.values.get("chapter_id"))
    status=request.values.get("status")
    ChapterService.update_chapter(chapter_id, "status", status)

    story = StoryService.get_story(story_id)
    chapter= ChapterService.get_chapter(chapter_id)
    dl_name = f"{story.title} {chapter.title}"
    logging.debug(f"Summarising {dl_name}")

    if story_id and chapter_id:
        try:
            summary, disp_summary = build_summary(story, chapter)

            flash("Chapter summarised", "success")
            messages = get_flashed_messages(with_categories=True)
            return ({"success": True, "summary" : summary, "disp_summary" : disp_summary, "messages" : messages}), 200
        except Exception as e:
            logging.debug(f"Error {e}")
            return jsonify({"success": False, "message": "Summary generation failed"}), 406
    else:
        return jsonify({"success": False, "message": "Missing story or chapter id"}), 406

def build_summary(story, chapter):
    posts=PostService.get_chapter_posts(story.story_id, chapter.chapter_id)
    chars_list=ChapterCharService.get_chapter_chars(story.story_id, chapter.chapter_id)
    chars=[]
    for char in chars_list:
        character = CharService.get_character(char.char_id)
        chars.append({
            "name": character.name,
            "note" : char.note
        })
    previous=ChapterService.get_previous_chapter_summary(story.story_id, chapter.position)

    prompt=render_template("prompts/summariseChapter.txt", story=story, chapter=chapter, chars=chars, previous=previous, posts=posts)
    summary_instruction=render_template("prompts/summariseInstruction.txt")
    chat=get_chat_service()
    chat.reset_chat(story, summary_instruction)
    chat.add_history("user", prompt)
    summary = chat.send_message(prompt)

    ChapterService.update_chapter(chapter.chapter_id, "summary", summary)

    return summary, markdown.markdown(summary)