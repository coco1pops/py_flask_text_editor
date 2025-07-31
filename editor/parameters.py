from flask import (Flask, Blueprint, render_template, request, redirect, url_for, jsonify, current_app)

import os

import editor.db

app = Flask(__name__)
bp = Blueprint("parameters", __name__)
#
# Creates a new character
#
@bp.route("/createchar/<int:char_id>", methods=["GET", "POST"])
@bp.route("/createchar", methods=["GET", "POST"])
def createchar(char_id=None):
    print (f"{request.method} char id {char_id}")
    if char_id:
        char=editor.db.get_character(char_id)
        print (f"Character {char['char_id']}")
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

        print(f"After POST char id {char_id}")
        if char_id == None:
            print ("Insert")
            char_id = editor.db.insert_character(name, description, personality, motivation)
            print (f"Inserted row {char_id}")
            if image_file:
                editor.db.update_character_image(char_id,image_bytes, mimeType)
            char = editor.db.get_character(char_id)
        else:
            print ("Update")
            editor.db.update_all_character(char_id, name, description, personality, motivation)
            if image_file:
                editor.db.update_character_image(char_id,image_bytes, mimeType)
            char = editor.db.get_character(char_id)

        return redirect(url_for('parameters.createchar', char_id=char_id))

    return render_template("parameters/create_character.html", char=char)

@bp.route("/getchar")
def getchar():
    char_id=request.values.get("char_id")
    row=editor.db.get_character(char_id)
    if row['image_mime_type'] != "":
        row['image_data'] ="data:" + row['image_mime_type'] + ";base64,{" + base64.b64encode(row['image_data']).decode('utf-8') +"}"

    return jsonify(row), 200

@bp.route("/deletechar",methods=["POST"])
def delchar():
    char_id=request.values.get("char_id")
    print (f"char id {char_id}")
    editor.db.delete_character(char_id)
    return jsonify({"response" : "Success"}), 200

@bp.route("/chars", methods=["GET", "POST"])
def chars():
    chars = editor.db.get_characters()
    if request.method == "POST":
        char_id = request.form.get("action")
        return redirect(url_for('parameters.createchar', char_id=char_id))

    return render_template("parameters/chars.html", chars=chars)

@bp.route("/checkimage", methods=["POST"])
def checkimage():
    f = request.files["file"]
    print (f"filename {f.filename}")

    ext = os.path.splitext(f.filename)[1]
    ext = ext.lower()
    if ext not in current_app.config['UPLOAD_EXTENSIONS']:
        return "Unsupported file type", 400
    
    return jsonify({'status': 'success', 'message': 'File valid'})

