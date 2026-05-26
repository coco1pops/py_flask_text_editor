from flask import (
    Flask,
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    current_app,
    flash,
    get_flashed_messages,
    abort,
)
from flask_login import login_required, current_user

from editor.utils.decorators import admin_required

from editor.models.chars import CharService
from editor.models.users import UserService
from editor.models.sysints import SysIntService
from editor.models.storyChars import StoryCharsService
from editor.utils.processImage import process_image

import os
import logging
import base64


app = Flask(__name__)
bp = Blueprint("parameters", __name__)


#
# Creates a new character
#
@bp.route("/createchar/<int:char_id>", methods=["GET", "POST"])
@bp.route("/createchar", methods=["GET", "POST"])
@login_required
def createchar(char_id=None):
    if char_id:
        char = CharService.get_character_formatted(char_id)
        logging.debug(f"Updating character {char['char_id']}")
    else:
        char = None

    if request.method == "POST":
        name = request.form["name"] or "Anonymous"
        description = request.form["description"] or ""
        personality = request.form["personality"] or ""
        motivation = request.form["motivation"] or ""
        image_file = request.files.get("image")
        if image_file:
            image_bytes, mimeType = process_image(image_file)

        if char_id == None:
            logging.debug("Inserting new character")
            char_id = CharService.insert_character(
                name, description, personality, motivation
            )
            logging.debug(f"Inserted character {char_id}")
            if image_file:
                CharService.update_character_image(char_id, image_bytes, mimeType)
            char = CharService.get_character(char_id)
            flash("Character added", "success")
        else:
            logging.debug(f"Updated character {char_id}")
            CharService.update_character_all(
                char_id, name, description, personality, motivation
            )
            if image_file:
                CharService.update_character_image(char_id, image_bytes, mimeType)
            char = CharService.get_character(char_id)
            flash("Character updated", "success")

        return redirect(url_for("parameters.createchar", char_id=char_id))

    return render_template("parameters/charCreate.html", char=char)


@bp.route("/getchar")
@login_required
def getchar():
    char_id = int(request.values.get("char_id"))
    row = CharService.get_character(char_id)
    if row.image_mime_type:
        row.image_data = (
            "data:"
            + row.image_mime_type
            + ";base64,{"
            + base64.b64encode(row.image_data).decode("utf-8")
            + "}"
        )

    return jsonify(row), 200


@bp.route("/deletechar", methods=["POST"])
@login_required
def delchar():
    char_id = int(request.values.get("char_id"))
    logging.debug(f"Deleting character {char_id}")
    
    if StoryCharsService.get_story_chars_for_char(char_id):
        flash("Cannot delete - character linked to story", "error")
        success=False
        
    else:
        try:
            CharService.delete_character(char_id)
            flash("Character deleted", "success")
            success=True
        except Exception as e:
            logging.debug(f"Error {e}")
            return jsonify({"success": False, "message": "Database delete failed"}), 462

    messages = get_flashed_messages(with_categories=True)
    return jsonify({"success" : success, "messages": messages}), 200


@bp.route("/chars", methods=["GET", "POST"])
@login_required
def chars():
    chars = CharService.get_characters()
    if request.method == "POST":
        char_id = int(request.form.get("action"))
        return redirect(url_for("parameters.createchar", char_id=char_id))

    return render_template("parameters/charsList.html", chars=chars)


@bp.route("/checkimage", methods=["POST"])
@login_required
def checkimage():
    f = request.files["file"]
    logging.debug(f"Checking image filename {f.filename}")

    ext = os.path.splitext(f.filename)[1]
    ext = ext.lower()
    if ext not in current_app.config["UPLOAD_EXTENSIONS"]:
        return "Unsupported file type", 400

    return jsonify({"status": "success", "message": "File valid"}), 200

@bp.route("/build_char_list_item", methods=["POST"])
@login_required
def build_char_list_item():
    char_id = int(request.values["char_id"])
    input_name = request.values.get("input_name")
    dropdown_id = request.values.get("dropdown_id")

    logging.debug(f"Building char list for character {char_id}, input name {input_name} and dropdown {dropdown_id}")
    if char_id:
        char = CharService.get_character(char_id)
        list_item = render_template("parameters/charDropdownItemStub.html", char=char, input_name=input_name, dropdown_id=dropdown_id)
        return jsonify({"success": True, "message" : "List item built", "listItem": list_item}), 200

    return jsonify({"success": False, "message": "Missing character id"}), 406


@bp.route("/createuser/<mode>/<user_id>", methods=["GET", "POST"])
@bp.route("/createuser", methods=["GET", "POST"])
@login_required
def createuser(mode="Add", user_id=None):
    if user_id and mode == "Update":
        if current_user.id != user_id and not current_user.is_admin:
            abort(403)
        user = UserService.get_user(user_id)
        logging.debug(f"Updating user {user.user_id}")
    else:
        if not current_user.is_admin:
            abort(403)
        user = None
        mode = "Add"

    if request.method == "POST":
        action = request.form.get("action")

        if mode == "Add":
            user_id = request.form["user_id"]
            user_password = request.form["user_password"]
            user_name = request.form["user_name"] or "Anonymous"
            user_role = request.form["user_role"]
        elif action == "main":
            user_name = request.form["user_name"] or "Anonymous"
            user_role = request.form["user_role"]
        elif action == "reset":
            new_password = request.form["new_password"]
            conf_password = request.form["conf_password"]

        fail = False

        if mode == "Add":
            if len(user_id) < 4 or len(user_id) > 20:
                flash("Invalid user id", "danger")
                fail = True
            if len(user_password) < 6 or len(user_password) > 20:
                flash("Invalid password", "danger")
                fail = True
            tst = UserService.get_user(user_id, allow_not_found=True)
            if tst:
                flash("User already exists", "danger")
                fail = True

        elif action == "reset":
            if len(new_password) < 6 or len(new_password) > 20:
                flash("Invalid password", "danger")
                fail = True
            if new_password != conf_password:
                flash("Passwords don't match", "danger")
                fail = True

        if fail:
            if mode == "Add":
                format_user = {
                    "user_id": user_id,
                    "user_password": user_password,
                    "user_name": user_name,
                    "user_role": user_role,
                }
            elif action == "main":
                format_user = {
                    "user_id": user_id,
                    "user_name": user_name,
                    "user_role": user_role,
                }
            else:
                tst =UserService.get_user(user_id)
                user_name = tst.user_name
                user_role = tst.user_role
                format_user = {
                    "user_id": user_id,
                    "user_name": user_name,
                    "user_role": user_role,
                    "new_password": new_password,
                    "conf_password": conf_password,
                }
            return render_template(
                "parameters/userCreate.html", mode=mode, user=format_user
            )

        if mode == "Add":
            logging.debug("Inserting new user")
            user_id = UserService.insert_user(
                user_id, user_password, user_name, user_role
            )
            logging.debug(f"Inserted user {user_id}")
            flash("User added", "success")
        else:
            if action == "main":
                logging.debug(f"Updated user {user_id}")
                UserService.update_user(user_id, user_name, user_role)
                flash("User updated", "success")
            else:
                UserService.user_reset_pass(user_id, new_password)
                flash("Password reset", "success")
        return redirect(
            url_for("parameters.createuser", mode="Update", user_id=user_id)
        )

    return render_template("parameters/userCreate.html", mode=mode, user=user)


@bp.route("/deleteuser", methods=["POST"])
@admin_required
def deluser():
    user_id = request.values.get("user_id")
    logging.debug(f"Deleting user {user_id}")

    try:
        UserService.delete_user(user_id)
        flash("User deleted", "success")
        messages = get_flashed_messages(with_categories=True)
        return jsonify({"success": True, "messages": messages}), 200
    
    except Exception as e:
        logging.error(f"Error deleting user {user_id}: {e}")
        return jsonify({"success": False, "message": "Database delete failed"}), 462


@bp.route("/users", methods=["GET", "POST"])
@admin_required
def users():
    users = UserService.get_users()
    if request.method == "POST":
        user_id = request.form.get("action")
        return redirect(
            url_for("parameters.createuser", mode="Update", user_id=user_id)
        )

    return render_template("parameters/usersList.html", users=users)


@bp.route("/sysints", methods=["GET", "POST"])
@admin_required
def sysints():
    sysints = SysIntService.get_sysints()
    if request.method == "POST":
        sysint_id = request.form.get("action")
        return redirect(url_for("parameters.createsysint", sysint_id=sysint_id))

    return render_template("parameters/sysintsList.html", sysints=sysints)


@bp.route("/deletesysint", methods=["POST"])
@admin_required
def delsysint():
    sysint_id = int(request.values.get("sysint_id"))
    logging.debug(f"Deleting sysint {sysint_id}")
    try:
        SysIntService.delete_sysint(sysint_id)
        flash("AI Guidance deleted", "success")
        messages = get_flashed_messages(with_categories=True)
        return jsonify({"success": True, "messages": messages}), 200
    except Exception as e:
        logging.error(f"Error deleting sysint {sysint_id}: {e}")
        return jsonify({"success": False, "message": "Database delete failed"}), 462


@bp.route("/createsysint/<int:sysint_id>", methods=["GET", "POST"])
@bp.route("/createsysint", methods=["GET", "POST"])
@admin_required
def createsysint(sysint_id=None):
    if sysint_id:
        sysint = SysIntService.get_sysint(sysint_id)
        logging.debug(f"Updating sysint {sysint.sysint_id}")
    else:
        sysint = None

    if request.method == "POST":
        name = request.form["name"] or "Not Given"
        description = request.form["description"] or ""
        instruction = request.form["instruction"] or ""

        if sysint_id == None:
            logging.debug("Inserting new sysint")
            try:
                sysint_id = SysIntService.insert_sysint(name, description, instruction)
                logging.debug(f"Inserted sysint {sysint_id}")
                flash("AI Guidance added", "success")
            except Exception as e:
                logging.error(f"Error inserting sysint: {e}")
                flash("Failed to add AI Guidance", "error")
        else:
            logging.debug(f"Updating sysint {sysint_id}")
            try:
                SysIntService.update_sysint(sysint_id, name, description, instruction)
                flash("AI Guidance updated", "success")
            except Exception as e:
                logging.error(f"Error updating sysint {sysint_id}: {e}")
                flash("Failed to update AI Guidance", "error")

        return redirect(url_for("parameters.createsysint", sysint_id=sysint_id))

    return render_template("parameters/sysintCreate.html", sysint=sysint)


@bp.route("/getSysInt", methods=["POST"])
@login_required
def getsysint():
    sysint_id = int(request.values.get("sysint_id"))
    row = SysIntService.get_sysint(sysint_id)
    return ({"success": True, "instruction": row.instruction}), 200
