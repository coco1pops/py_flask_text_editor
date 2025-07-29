from flask import (Blueprint, redirect, render_template, request, url_for, jsonify)

from editor.database import get_db
from editor.chat_service import get_chat_service

from google import genai

import markdown

bp = Blueprint("stories", __name__)
#
# Creates a new story and adds a system instruction record
#
@bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        author = request.form["author"] or "Anonymous"
        story = request.form["title"]
        note = request.form["note"] or ""
        systemInstruction = request.form["systemInstruction"] or ""

        if story:
            db = get_db()
            story_id = db.execute(
                "INSERT INTO stories (author, title, note, systemInstruction) VALUES (?, ?, ? ,?)",
                (author, story, note, systemInstruction),
            ).lastrowid
            db.commit()

            return redirect(url_for("stories.generate_story", story_id=story_id))
        
    return render_template("stories/create.html")

# Returns a list of stories
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
#
# Deletes a story and related posts
#
@bp.route("/delete_story", methods=["POST"])
def delete_story():
    story_id=request.values.get("story_id")
    print(f"Requested delete of row {story_id}")
    if story_id:
        db = get_db()
        db.execute(
            "DELETE FROM posts WHERE story_id=(?)", (story_id,)
        )
        db.commit()
        db.execute(
            "DELETE FROM stories WHERE story_id=(?)",(story_id,))
        db.commit()
        return jsonify({'success': 'Record deleted'}), 200
    return jsonify({'error': 'Database delete failed'}), 406
#
# Updates an individual story
#
@bp.route("/update_story", methods=["POST"])
def update_story():
    story_id = request.values.get("story_id")
    field = request.values.get("field")
    value = request.values.get("new value")

    print (f"Updating {story_id} {field} {value}")
    if story_id:
        db = get_db()
        db.execute(
            f"UPDATE stories SET {field} = (?) WHERE story_id = (?)", ( value, story_id)
            )
        if field == 'systemInstruction':
            db.execute(
                "UPDATE posts SET message = (?) WHERE story_id = (?) and creator = (?)", (value, story_id, "system",)
                )
        db.commit()
        return jsonify({'success': 'Record udpdated'}), 200
    return jsonify({'error': 'Database update failed'}), 406
#
# Used to display an individual story and the chat. Behind the scenes it also populates the chat with previous messages
#
@bp.route("/generate_story")
def generate_story():
    story_id=request.values.get("story_id")
        
    db = get_db()
    story=db.execute(
        "SELECT story_id, author, title, note, systemInstruction, created FROM stories WHERE story_id = (?)", (story_id,)).fetchone()
    posts = db.execute(
        "SELECT post_id, created, creator, message FROM posts where story_id = (?) ORDER BY created ASC", (story_id,)).fetchall()
    
    format_posts = []
    for row, post in enumerate(posts):
        format_posts.append({'post_id' : post['post_id'], 'created' : post['created'], 'creator' : post['creator'], 'message' : markdown.markdown(post['message'])})

    return render_template("stories/generate_story.html",story=story, posts=format_posts)

@bp.route("/get_message", methods=["GET"])
def get_message():
    post_id = request.values.get("post_id")

    print (f"Retrieving {post_id}")
    if post_id:
        db = get_db()
        row=db.execute(
            "SELECT message from posts WHERE post_id = (?)", ( post_id,)).fetchone()
        return jsonify({"message": row['message']}), 200
    return jsonify({'error': 'Database update failed'}), 406


#
# Generates a chat line from a prompt and inserts the response into the database
#
@bp.route("/generate", methods=["POST"])
def generate_text():
    story_id = request.values.get("story_id")
    prompt = request.values.get("prompt")
    mode = request.values.get("mode")
    row_id = request.values.get("row_id")

    if not prompt:
        return jsonify({"error": "Invalid input. Please provide a JSON object with a 'prompt' key."}), 400
    
    print(f"Received prompt: '{prompt}', Mode '{mode}' Row '{row_id}'")
    #
    # First amend the database to reflect the changes
    #
    inserted_id=-1
    if mode == "New":
        try:
            db=get_db()
            inserted_id=db.execute (
                "INSERT INTO posts (story_id, creator, message) VALUES (?, ?, ?)", (story_id, "user", prompt)
            ).lastrowid
            db.commit()
            print (f"Last Row {inserted_id}")

        except Exception as e:
            print (f"Insert Exception {e}")
            return jsonify({'error': 'Prompt insert failed'}), 406

    elif mode == "Edit Response":
        try:
            db=get_db()
            db.execute (
                "UPDATE posts SET (message) = (?) WHERE post_id = (?)", (prompt, row_id)           
            )
            db.commit()
        except:
            return jsonify({'error': 'Prompt update failed'}), 406

    elif mode == "Edit Prompt":
        try:
            db=get_db()
            db.execute (
                "DELETE FROM posts WHERE story_id = (?) and post_id >= (?)", (story_id, row_id,)           
            )
            db.commit()

            inserted_id=db.execute (
                "INSERT INTO posts (story_id, creator, message) VALUES (?, ?, ?)", (story_id, "user", prompt)
            ).lastrowid
            db.commit()
        except:
            return jsonify({'error': 'Prompt delete failed'}), 406   
    else:
        return jsonify({'error': 'Invalid mode'}), 406
    #
    # Next build the history
    #
    chat = get_chat_service()
    db=get_db()
    story=db.execute("SELECT systemInstruction from stories where story_id=(?)", (story_id,)).fetchone()
    chat.reset_chat(story['systemInstruction'])

    try:
        db=get_db()
        posts = db.execute (
                "SELECT post_id, creator, message FROM posts WHERE story_id = (?) ORDER BY post_id ASC", (story_id,)           
            ).fetchall()
    except:
        return jsonify({'error': 'Retrieving Posts'}), 406 

    print ("Retrieved Posts")
    for post in posts:
        if post['post_id'] != inserted_id or mode == "Edit Response": # Don't include latest post
            chat.add_history(post['creator'], post['message'])

    if mode == "Edit Response":
        return jsonify({'success': 'Prompt Updated'}), 200
    
    print ("Trying to send prompt")
    #
    # Need to generate new content
    #    
    try:
        # Generate content
        message = chat.send_message(prompt)
    
    except Exception as e:
        print(f"Error generating content: {e}")
        print("Exception Type:", type(e).__name__)
        print("Exception Message:", str(e))

        return jsonify({"error": str(e)}), 500
    
    if message:
        try:
            db=get_db()
            db.execute(
                "INSERT INTO posts (story_id, creator, message) VALUES (?, ?, ?)", (story_id, "model", message)
            )
            db.commit()
        except Exception as e:
            print(f"Error adding prompt")
            return jsonify({"error": str(e)}), 500

        return jsonify({'success': 'New Response Added'}), 200

'''//       return jsonify({"response": response_text})'''
