from flask import (Blueprint, render_template, request, redirect, url_for)
import editor.db

bp = Blueprint("parameters", __name__)
#
# Creates a new character
#
@bp.route("/createchar", methods=["GET", "POST"])
def createchar():
    if request.method == "POST":
        name = request.form["name"] or "Anonymous"
        description = request.form["description"] or ""
        personality = request.form["personality"] or ""
        motivation = request.form["motivation"] or ""

        editor.db.insert_character(name, description, personality, motivation,"","")

        return redirect(url_for("parameters.characters"))
        
    return render_template("parameters/create_character.html")

@bp.route("/characters")
def characters():
    return render_template("parameters/characters.html")