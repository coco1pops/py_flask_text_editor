import logging

from flask import (
    Blueprint,
    request,
    jsonify,
    url_for,
    redirect
)
from flask_login import current_user

from editor.models.storyChars import StoryCharsService, StoryWithCharactersService
from editor.models.stories import StoryService

bp = Blueprint("storyCharacters", __name__)
@bp.before_request
def require_login():
    if not current_user.is_authenticated:
        logging.debug("Not authenticated")
        return redirect(url_for("login.login"))  # Redirect to your login route

@bp.route("/addStoryCharacter", methods=["POST"])
def add_story_character():
    logging.debug(f"Adding story character with values {request.values["story_id"]} {request.values["char_id"]} {request.values["char_notes"]}")
    story_id = int(request.values["story_id"])
    story = StoryService.get_user_story(story_id, current_user.id)
    if not story:
        logging.error(f"Error occurred while fetching story")
        return jsonify({"success": False, "message": "Story not found or access denied"}), 404
    
    char_id = int(request.values["char_id"])
    char_notes = request.values["char_notes"]

    logging.debug(f"Adding char {char_id} to story {story_id} with notes {char_notes}")
    if story_id and char_id:
        try:
            new_id = StoryCharsService.insert_story_char(story_id, char_id, char_notes)
        except Exception as e:
            logging.error(f"Error adding story character: {e}")
            return jsonify({"success": False, "message": "Database Add Failed"}), 406

        if new_id:
            storyChar=StoryWithCharactersService.get_story_with_character(new_id)
            logging.debug(f"New story char {storyChar.id} for story {storyChar.story_id} char {storyChar.char_id} {storyChar.name} with notes {storyChar.note}")
            return jsonify({"success": True, "message": "Character added successfully", "id": new_id,     
                "storyChar": {
                    "name": storyChar.name,
                    "description": storyChar.description,
                    "note": storyChar.note
                }}), 200
        else:
            return jsonify({"success": False, "message": "Failed to add character to story"}), 406

    return jsonify({"success": False, "message": "Missing story id or character id"}), 406  

@bp.route("/updateStoryCharacter", methods=["POST"])    
def update_story_character():
    id = int(request.values["id"])
    record = StoryWithCharactersService.get_story_with_character(id)
    story=StoryService.get_user_story(record.story_id, current_user.id)
    if not story:
        logging.error(f"Error occurred while fetching story")
        return jsonify({"success": False, "message": "Story not found or access denied"}), 404

    char_notes = request.values["note"]

    logging.debug(f"Updating story char {id} with notes {char_notes}")
    if id:
        try:
            StoryCharsService.update_story_char(id, char_notes)
            return jsonify({"success": True, "message": "Character updated successfully"}), 200
        except Exception as e:
            logging.error(f"Error updating story character: {e}")
            return jsonify({"success": False, "message": "Database Update Failed"}), 406

    return jsonify({"success": False, "message": "Missing story character id"}), 406

@bp.route("/deleteStoryCharacter", methods=["POST"])
def delete_story_character():
    story_char_id = int(request.values["id"])
    story_char=StoryWithCharactersService.get_story_with_character(story_char_id)
    story=StoryService.get_user_story(story_char.story_id, current_user.id)
    if not story:
        logging.error(f"Error occurred while fetching story")
        return jsonify({"success": False, "message": "Story not found or access denied"}), 404
    char_id=story_char.char_id

    logging.debug(f"Deleting story char {story_char_id}")
    if story_char_id:
        try:
            StoryCharsService.delete_story_char(story_char_id)
            return jsonify({"success": True, "message": "Character deleted successfully", "char_id": char_id}), 200
        except Exception as e:
            logging.error(f"Error deleting story character: {e}")
            return jsonify({"success": False, "message": "Database Delete Failed"}), 406

    return jsonify({"success": False, "message": "Missing story character id"}), 406

@bp.route("/getStoryCharacter", methods=["POST"])
def get_story_character():
    story_char_id = int(request.values["id"])

    logging.debug(f"Getting story char {story_char_id}")
    if story_char_id:
        storyChar = StoryWithCharactersService.get_story_with_character(story_char_id)
        story = StoryService.get_user_story(storyChar.story_id, current_user.id)
        if not story:
            logging.error(f"Error occurred while fetching story")
            return jsonify({"success": False, "message": "Story not found or access denied"}), 404  
        
        if storyChar:
            return jsonify({"success": True, "message": "Character found", "storyChar": {
                    "name": storyChar.name,
                    "description": storyChar.description,
                    "note": storyChar.note
                }}), 200

    return jsonify({"success": False, "message": "Missing story character id"}), 406