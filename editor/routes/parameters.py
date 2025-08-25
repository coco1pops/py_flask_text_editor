from flask import (Flask, Blueprint, render_template, request, redirect, url_for, jsonify, current_app, flash, get_flashed_messages, abort)
from flask_login import login_required, current_user

from editor.utils.decorators import admin_required

import os
import logging
import base64

import editor.db

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
        char=editor.db.get_character(char_id)
        logging.debug (f"Updating character {char['char_id']}")
    else:
        char=None
        
    if request.method == "POST":
        name = request.form["name"] or "Anonymous"
        description = request.form["description"] or ""
        personality = request.form["personality"] or ""
        motivation = request.form["motivation"] or "" 
        image_file = request.files.get('image')
        if image_file:
            image_bytes = image_file.read()
            mimeType = image_file.mimetype

        if char_id == None:
            logging.debug("Inserting new character")
            char_id = editor.db.insert_character(name, description, personality, motivation)
            logging.debug(f"Inserted character {char_id}")
            if image_file:
                editor.db.update_character_image(char_id,image_bytes, mimeType)
            char = editor.db.get_character(char_id)
            flash('Character added', "success")
        else:
            logging.debug(f"Updated character {char_id}")
            editor.db.update_all_character(char_id, name, description, personality, motivation)
            if image_file:
                editor.db.update_character_image(char_id,image_bytes, mimeType)
            char = editor.db.get_character(char_id)
            flash('Character updated', "success")

        return redirect(url_for('parameters.createchar', char_id=char_id))

    return render_template("parameters/create_character.html", char=char)

@bp.route("/getchar")
@login_required
def getchar():
    char_id=request.values.get("char_id")
    row=editor.db.get_character(char_id)
    if row['image_mime_type'] != "":
        row['image_data'] ="data:" + row['image_mime_type'] + ";base64,{" + base64.b64encode(row['image_data']).decode('utf-8') +"}"

    return jsonify(row), 200

@bp.route("/deletechar",methods=["POST"])
@login_required
def delchar():
    char_id=request.values.get("char_id")
    logging.debug(f"Deleting character {char_id}")
    editor.db.delete_character(char_id)
    flash('Character deleted', "success")
    messages = get_flashed_messages(with_categories=True)
    return jsonify({"messages": messages})

@bp.route("/chars", methods=["GET", "POST"])
@login_required
def chars():
    chars = editor.db.get_characters()
    if request.method == "POST":
        char_id = request.form.get("action")
        return redirect(url_for('parameters.createchar', char_id=char_id))

    return render_template("parameters/chars.html", chars=chars)

@bp.route("/checkimage", methods=["POST"])
@login_required
def checkimage():
    f = request.files["file"]
    logging.debug(f"Checking image filename {f.filename}")

    ext = os.path.splitext(f.filename)[1]
    ext = ext.lower()
    if ext not in current_app.config['UPLOAD_EXTENSIONS']:
        return "Unsupported file type", 400
    
    return jsonify({'status': 'success', 'message': 'File valid'})

@bp.route("/createuser/<mode>/<user_id>", methods=["GET", "POST"])
@bp.route("/createuser", methods=["GET", "POST"])
@login_required
def create_user(mode="Add", user_id=None):
    if user_id and mode=="Update":
        if current_user.id != user_id and not current_user.is_admin:
            abort(403)
        user=editor.db.get_user(user_id)
        logging.debug (f"Updating user {user['user_id']}")
    else:
        if not current_user.is_admin:
            abort(403)
        user=None
        mode="Add"

    if request.method == "POST":
        action = request.form.get('action')

        if mode=="Add":
            user_id = request.form["user_id"]
            user_password = request.form["user_password"]
            user_name = request.form["user_name"] or "Anonymous"
            user_role = request.form["user_role"]
        elif action=="main":
            user_name = request.form["user_name"] or "Anonymous"
            user_role = request.form["user_role"]
        elif action=="reset":
            new_password = request.form["new_password"]
            conf_password = request.form["conf_password"]

        fail=False

        if mode=="Add":
            if len(user_id) < 4 or len(user_id)>20:
                flash('Invalid user id', "danger")
                fail=True
            if len(user_password) < 6 or len (user_password) > 20:
                flash('Invalid password', "danger")
                fail=True
            tst=editor.db.get_user(user_id,allow_not_found=True)
            if tst:
                flash('User already exists', "danger")
                fail=True

        elif action=="reset":
            if len(new_password) < 6 or len (new_password) > 20:
                flash('Invalid password', "danger")
                fail=True
            if new_password != conf_password:
                flash("Passwords don't match", "danger")
                fail=True

        if fail:
            if mode == "Add":
                format_user=({"user_id" : user_id, "user_password" : user_password, "user_name" : user_name, "user_role" : user_role })
            elif action == "main":
                format_user=({"user_id" : user_id, "user_name" : user_name, "user_role" : user_role })
            else:
                tst=editor.db.get_user(user_id)
                user_name=tst['user_name']
                user_role=tst['user_role']
                format_user=({"user_id" : user_id, "user_name" : user_name, "user_role" : user_role, "new_password" : new_password, "conf_password" : conf_password})
            return render_template("parameters/create_user.html", mode=mode, user=format_user)
        
        if mode == "Add":
            logging.debug("Inserting new user")
            user_id = editor.db.insert_user(user_id, user_password, user_name, user_role)
            logging.debug(f"Inserted user {user_id}")
            flash('User added', "success")
        else:
            if action=="main":
                logging.debug(f"Updated user {user_id}")
                editor.db.update_user(user_id, user_name, user_role)
                flash('User updated', "success")
            else:
                editor.db.user_reset_pass(user_id, new_password)
                flash('Password reset', "success")
        return redirect(url_for('parameters.create_user', mode="Update", user_id=user_id))

    return render_template("parameters/create_user.html", mode=mode, user=user)

@bp.route("/deleteuser",methods=["POST"])
@admin_required
def deluser():
    user_id=request.values.get("user_id")
    logging.debug(f"Deleting user {user_id}")
    editor.db.delete_user(user_id)
    flash('User deleted', "success")
    messages = get_flashed_messages(with_categories=True)
    return jsonify({"messages": messages})

@bp.route("/users", methods=["GET", "POST"])
@admin_required
def users():
    users = editor.db.get_users()
    if request.method == "POST":
        user_id = request.form.get("action")
        return redirect(url_for('parameters.create_user',mode="Update", user_id=user_id))

    return render_template("parameters/users.html", users=users)

@bp.route("/sysints", methods=["GET", "POST"])
@admin_required
def sysints():
    sysints = editor.db.get_sysints()
    if request.method == "POST":
        sysint_id = request.form.get("action")
        return redirect(url_for('parameters.createsysint', sysint_id=sysint_id))

    return render_template("parameters/sysints.html", sysints=sysints)

@bp.route("/deletesysint",methods=["POST"])
@admin_required
def delsysint():
    sysint_id=request.values.get("sysint_id")
    logging.debug(f"Deleting sysint {sysint_id}")
    editor.db.delete_sysint(sysint_id)
    flash('AI Guidance deleted', "success")
    messages = get_flashed_messages(with_categories=True)
    return jsonify({"messages": messages})

@bp.route("/createsysint/<int:sysint_id>", methods=["GET", "POST"])
@bp.route("/createsysint", methods=["GET", "POST"])
@admin_required
def createsysint(sysint_id=None):
    if sysint_id:
        sysint=editor.db.get_sysint(sysint_id)
        logging.debug (f"Updating sysint {sysint['sysint_id']}")
    else:
        sysint=None
        
    if request.method == "POST":
        name = request.form["name"] or "Not Given"
        description = request.form["description"] or ""
        instruction = request.form["instruction"] or ""

        if sysint_id == None:
            logging.debug("Inserting new sysint")
            sysint_id = editor.db.insert_sysint(name, description, instruction)
            logging.debug(f"Inserted sysint {sysint_id}")
            flash('AI Guidance added', "success")
        else:
            logging.debug(f"Updated sysint {sysint_id}")
            editor.db.update_sysint(sysint_id, name, description, instruction)
            sysint = editor.db.get_sysint(sysint_id)
            flash('AI Guidance updated', "success")

        return redirect(url_for('parameters.createsysint', sysint_id=sysint_id))

    return render_template("parameters/create_sysint.html", sysint=sysint)

@bp.route("/getSysInt",methods=["POST"])
@admin_required
def getsysint():
    sysint_id=request.values.get("sysint_id")
    row=editor.db.get_sysint(sysint_id)
    return ({"instruction":row['instruction']}), 200


