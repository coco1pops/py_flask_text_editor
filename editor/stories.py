from flask import (Blueprint, redirect, render_template, request, url_for, jsonify)

from editor.database import get_db
from editor.auth import model

from google import genai
from google.genai.types import HttpOptions

import markdown

bp = Blueprint("stories", __name__)

@bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        author = request.form["author"] or "Anonymous"
        story = request.form["title"]
        note = request.form["note"] or ""
        systemInstruction = request.form["systemInstruction"] or ""

        if story:
            db = get_db()
            db.execute(
                "INSERT INTO stories (author, title, note, systemInstruction) VALUES (?, ?, ? ,?)",
                (author, story, note, systemInstruction),
            )
            db.commit()
            return redirect(url_for("stories.stories"))
        
    return render_template("stories/create.html")

@bp.route("/stories", methods=["GET", "POST"])
def stories():
    if request.method == "POST":
        story_id = request.form.get("action")
        return redirect(url_for("stories.generate_story", story_id=story_id))

    db = get_db()
    stories = db.execute(
        "SELECT story_id, author, title, note, created FROM stories ORDER BY created DESC"
    ).fetchall()
    
    return render_template("stories/stories.html", stories=stories)

@bp.route("/delete_story", methods=["POST"])
def delete_story():
    story_id=request.values.get("id")
    if story_id:
        db = get_db()
        db.execute(
            "DELETE FROM stories WHERE story_id=(?)",(story_id,))
        db.commit()
        return jsonify({'success': 'Record deleted'}), 200
    return jsonify({'error': 'Database delete failed'}), 406

@bp.route("/generate_story")
def generate_story():
    story_id=request.values.get("story_id")
    
    db = get_db()
    story=db.execute(
        "SELECT story_id, author, title, note, systemInstruction, created FROM stories WHERE story_id = (?)", (story_id,)).fetchone()
    posts = db.execute(
        "SELECT post_id, created, prompt, message FROM posts where story_id = (?) ORDER BY created ASC", (story_id,)).fetchall()
    
    format_posts = []
    for row, post in enumerate(posts):
        format_posts.append({'post_id' : post['post_id'], 'created' : post['created'], 'message' : markdown.markdown(post['message'])})
      
    return render_template("stories/generate_story.html",story=story, posts=format_posts)

@bp.route("/update_story", methods=["POST"])
def update_story():
    story_id = request.values.get("story_id")
    field = request.values.get("field")
    value = request.values.get("new value")

    print (f"Updating {story_id} {field} {value}")
    if story_id:
        db = get_db()
        db.execute(
            f"UPDATE stories SET {field} = (?) WHERE story_id = (?)", ( value, story_id))
        db.commit()
        return jsonify({'success': 'Record deleted'}), 200
    return jsonify({'error': 'Database delete failed'}), 406

@bp.route("/generate", methods=["POST"])
def generate_text():

    story_id = request.values.get("story_id")
    prompt = request.values.get("prompt")
    if not prompt:
        return jsonify({"error": "Invalid input. Please provide a JSON object with a 'prompt' key."}), 400
    
    print(f"Received prompt: '{prompt}'")

    try:
        # Generate content
        response = model.generate_content(prompt)

        message = response.text
        print(f"GenAI response: '{message}'")

        if message:
            db=get_db()
            db.execute(
                "INSERT INTO posts (story_id, prompt, message) VALUES (?, ?, ?)", (story_id, prompt, message)
            )
            db.commit()

        return jsonify({'success': 'Response Received'}), 200
    
    except Exception as e:
        print(f"Error generating content: {e}")
        return jsonify({"error": str(e)}), 500
    
'''//       return jsonify({"response": response_text})'''
