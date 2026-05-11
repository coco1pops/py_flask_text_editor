import logging

from flask import (
    Blueprint,
    request,
    jsonify
)

from editor.models.storyChars import StoryCharsService, StoryWithCharactersService

bp = Blueprint("storyCharacters", __name__)

@bp.route("/addStoryCharacter", methods=["POST"])
def add_story_character():
    logging.debug(f"Adding story character with values {request.values["story_id"]} {request.values["char_id"]} {request.values["char_notes"]}")
    story_id = int(request.values["story_id"])
    char_id = int(request.values["char_id"])
    char_notes = request.values["char_notes"]

    logging.debug(f"Adding char {char_id} to story {story_id} with notes {char_notes}")
    if story_id and char_id:
        new_id = StoryCharsService.insert_story_char(story_id, char_id, char_notes)
        if new_id:
            storyChar=StoryWithCharactersService.get_story_with_character(new_id)
            logging.debug(f"New story char {storyChar.id} for story {storyChar.story_id} char {storyChar.char_id} {storyChar.name} with notes {storyChar.note}")
            return jsonify({"success": True, "id": new_id,     
                "storyChar": {
                    "name": storyChar.name,
                    "description": storyChar.description,
                    "note": storyChar.note
                }}), 200
        else:
            return jsonify({"error": "Failed to add character to story"}), 406

    return jsonify({"error": "Missing story id or character id"}), 406  

@bp.route("/updateStoryCharacter", methods=["POST"])    
def update_story_character():
    id = int(request.values["id"])
    char_notes = request.values["note"]

    logging.debug(f"Updating story char {id} with notes {char_notes}")
    if id:
        StoryCharsService.update_story_char(id, char_notes)
        return jsonify({"success": True}), 200

    return jsonify({"error": "Missing story character id"}), 406

@bp.route("/deleteStoryCharacter", methods=["POST"])
def delete_story_character():
    story_char_id = int(request.values["id"])

    logging.debug(f"Deleting story char {story_char_id}")
    if story_char_id:
        StoryCharsService.delete_story_char(story_char_id)
        return jsonify({"success": True}), 200

    return jsonify({"error": "Missing story character id"}), 406

@bp.route("/getStoryCharacter", methods=["POST"])
def get_story_character():
    story_char_id = int(request.values["id"])

    logging.debug(f"Getting story char {story_char_id}")
    if story_char_id:
        storyChar = StoryWithCharactersService.get_story_with_character(story_char_id)
        if storyChar:
            return jsonify({"success": True, "storyChar": {
                    "name": storyChar.name,
                    "description": storyChar.description,
                    "note": storyChar.note
                }}), 200

    return jsonify({"error": "Missing story character id"}), 406