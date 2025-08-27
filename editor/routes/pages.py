from flask import (Blueprint, render_template, request, redirect,url_for)
import editor.db
from flask_login import current_user

bp = Blueprint("pages", __name__)

@bp.route("/", methods=["GET", "POST"])
def home():
    if request.method=="POST":
        story_id=request.form.get('action')
        return redirect(url_for("stories.generate_story", story_id=story_id))
    if current_user.is_authenticated:
        latest_story = editor.db.get_latest_story()
        if latest_story:
            return render_template("pages/home.html",story=latest_story)
    return render_template("pages/home.html")


@bp.route("/about")
def about():
    return render_template("pages/about.html")

@bp.route("/instructions")
def instructions():
    return render_template("instructions/StoriesInstructions.html")