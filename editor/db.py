from editor.database import get_db
import base64
import markdown
import logging
#
# Character database functions
#
def get_characters():
    db = get_db()
    try:
        rows = db.execute("SELECT char_id, created, name, description from chars").fetchall()
        return rows
    except Exception as e:
        print_except("get_characters",e)
        return False

def get_character(char_id):
    
    try:         
        row = get_character_raw(char_id)
        
        image_data = None

        if row['image_mime_type'] != "":
            image_data ="data:" + row['image_mime_type'] + ";base64," + base64.b64encode(row['image_data']).decode('utf-8')
        
        format_row=({"char_id" : row['char_id'],"name": row['name'],"description": row['description'], "personality" : row['personality'], "motivation" : row['motivation'],
                           "image_data" : image_data, "image_mime_type" : row['image_mime_type']})

        return format_row
    except Exception as e:
        print_except("get_character",e)
        return False
    
def get_character_raw(char_id):
    db = get_db()
    try:         
        row = db.execute("SELECT char_id, name, description, personality, motivation, image_data, image_mime_type from chars WHERE char_id = (?)", 
                         (char_id,)).fetchone()
      
        return row
    except Exception as e:
        print_except("get_character",e)
        return False

def insert_character(name, description, personality, motivation):      
    db=get_db()
    try:
        row_id=db.execute(f"INSERT INTO chars (name, description, personality, motivation) VALUES (?, ?, ?, ?)", 
                   (name, description, personality, motivation,)).lastrowid
        db.commit()
        return row_id
    except Exception as e:
        print_except("insert_character",e)
        return False   

def update_character(char_id, field, value):
    db=get_db()
    try:
        db.execute(f"UPDATE chars SET ({field} = (?)) WHERE char_id = (?)", (value, char_id))
        db.commit()
        return True
    except Exception as e:
        print_except("update_character",e)
        return False
    
def update_all_character(char_id, name, description, personality, motivation):
    db=get_db()
    try:
        db.execute("UPDATE chars SET name = (?), description = (?), personality = (?), motivation = (?) WHERE char_id = (?)", 
                   (name, description, personality, motivation, char_id))
        db.commit()
        return True
    except Exception as e:
        print_except("update_all_character",e)
        return False

def update_character_image(char_id, image_data, image_mime_type):
    db=get_db()
    try:
        db.execute("UPDATE chars SET image_data = (?), image_mime_type = (?) WHERE char_id = (?)", 
                   (image_data, image_mime_type, char_id))
        db.commit()
        return True
    except Exception as e:
        print_except("update_image_character",e)
        return False

def delete_character(char_id):
    db=get_db()
    try:
        db.execute(f"DELETE from chars WHERE char_id = (?)", (char_id))
        db.commit()
        return True
    except Exception as e:
        print_except("delete_character",e)
        return False

def build_char(char_id):
    char = get_character(char_id)
    resp={"img": "", "image_mime_type" : "", "text" : ""}
    if char['image_mime_type'] != "":
        resp["image_mime_type"] = char['image_mime_type']
        resp["img"] = char["image_data"]
        resp["text"] = f"The picture shows <b>{char['name']}</b><br>"

    if char["description"] != "":
        resp["text"] = f"{resp['text']}<b>Description</b><br> {char['description']}"

    if char["personality"] != "":
        resp["text"] = f"{resp['text']}<br><b>Personality</b><br> {char['personality']}"

    if char["motivation"] != "":
        resp["text"] = f"{resp['text']}<br><b>Motivation</b><br> {char['motivation']}"
    
    return resp
#
# Story database functions
#

def get_story(story_id):
    try:
        db = get_db()
        story = db.execute(
            "SELECT story_id, author, title, note, systemInstruction, created FROM stories WHERE story_id =(?)", (story_id,)
            ).fetchone()
        return story
    except Exception as e:
        print_except("get_story",e)
        return False
    
def get_latest_story():
    try:
        db = get_db()
        story = db.execute (
            "SELECT story_id, author, title, note FROM stories WHERE created = (SELECT MAX(created) from stories)"
        ).fetchone()
        return story
    except Exception as e:
        print_except("get_latest_story", e)
        return False
    
def insert_story(author, title, note, systemInstruction):
    try:
        db = get_db()
        story_id = db.execute(
            "INSERT INTO stories (author, title, note, systemInstruction) VALUES (?, ?, ? ,?)",
            (author, title, note, systemInstruction),
        ).lastrowid
        db.commit()
        return story_id
    except Exception as e:
        print_except("insert_story",e)
        return False
    
def get_stories():
    try:
        db = get_db()
        stories = db.execute(
        "SELECT story_id, author, title, note, created FROM stories ORDER BY created DESC"
            ).fetchall()
        return stories
    except Exception as e:
        print_except("get_stories",e)
        return False
    
def delete_story(story_id):
    try:
        db = get_db()
        db.execute(
            "DELETE FROM posts WHERE story_id=(?)", (story_id,)
        )
        db.execute(
            "DELETE FROM post_parts WHERE story_id=(?)", (story_id,)
        )  
        db.execute(
            "DELETE FROM stories WHERE story_id=(?)",(story_id,))
        db.commit()
    except Exception as e:
        print_except("delete_story",e)
        return False

def update_story(story_id, field, value):
    db=get_db()
    try:
        db.execute(f"UPDATE stories SET {field} = (?) WHERE story_id = (?)", (value, story_id))
        db.commit()
        return True
    except Exception as e:
        print_except("update_story",e)
        return False
    
#
# Posts database functions
#

def get_message(post_id):
    db=get_db()
    try:
        row = db.execute("SELECT message FROM posts WHERE post_id = (?)", (post_id,)).fetchone()
        return row['message']

    except Exception as e:
        print_except("get_message",e)
        return False
    
def update_message(post_id, value):
    db=get_db()
    try:
        row = db.execute("UPDATE posts SET message = (?) WHERE post_id = (?)", (value, post_id,))
        db.commit()
        return True
    
    except Exception as e:
        print_except("update_message",e)
        return False

def get_all_posts(story_id):
    try:
        posts = get_all_posts_raw(story_id)
    
        format_posts = []
        posts_ix = 0
 
        for post in posts:

            message = ""
            upd = False
            if post['source'] =="post":
                message =  markdown.markdown(post['content'])
            if post['source'] == 'part' and post['part_type'] =='text':
                message =  markdown.markdown(post['part_text'])
            if post['source'] == 'part' and post['part_type'] == 'image' and post['part_image_mime_type'] != '':
                image_data ="data:" + post['part_image_mime_type'] + ";base64," + base64.b64encode(post['part_image_data']).decode('utf-8')
                upd=True
            else:
                image_data = ''
            
            if upd:
                format_posts[posts_ix - 1]['image_data'] = image_data
                format_posts[posts_ix - 1]['image_mime_type'] = post['part_image_mime_type']
            else:
                format_posts.append({'post_id' : post['post_id'], 'created' : post['created'], 'creator' : post['creator'],
                                  "multi_modal" : post['multi_modal'], "source" : post['source'], "part_type": post['part_type'], 
                                  "message" : message, 'image_data' : image_data, "image_mime_type" : post['part_image_mime_type']})
            
                posts_ix += 1

        return format_posts
    
    except Exception as e:
        print_except("get_all_posts",e)
        return False

def get_all_posts_raw(story_id):
    try:
        db = get_db()
        select_string = "SELECT post_id, created, creator, multi_modal, content, source, part_type, part_text, part_image_data, part_image_mime_type"
        select_string = f"{select_string} from unified_post_timeline WHERE story_id=(?) ORDER BY post_id, created ASC"
        posts = db.execute(select_string,(story_id,)).fetchall()
    
        return posts

    except Exception as e:
        print_except("get_all_posts_raw",e)
        return False

def delete_posts_from(story_id, post_id):
    try:
        db = get_db()
        db.execute(
            "DELETE FROM posts WHERE story_id=(?) AND post_id >= (?)", (story_id,post_id,)
        )
        db.execute(
            "DELETE FROM post_parts WHERE story_id=(?) AND post_id >= (?)", (story_id, post_id)
        )  
        db.commit()
    except Exception as e:
        print_except("delete_posts_from",e)
        return False

def insert_post(story_id, creator, prompt, multi):
    try:
        db=get_db()
        inserted_id=db.execute (
            "INSERT INTO posts (story_id, creator, message, multi_modal) VALUES (?, ?, ?, ?)", (story_id, creator, prompt, multi)
        ).lastrowid
        db.commit()
        return inserted_id
    except Exception as e:
        print_except("insert_post",e)
        return False

#
# Database functions for post parts
#
def insert_post_text_part(story_id, post_id, part_text):
    try:
        db=get_db()
        inserted_id=db.execute (
            "INSERT INTO post_parts (story_id, post_id, part_type, part_text) VALUES (?, ?, ?, ?)", (story_id, post_id, 'text', part_text)
        ).lastrowid
        db.commit()
        return inserted_id
    except Exception as e:
        print_except("insert_post_text_part",e)
        return False
    
def insert_post_image_part(story_id, post_id, part_image_data, part_image_mime_type):
    try:
        db=get_db()
        inserted_id=db.execute (
            "INSERT INTO post_parts (story_id, post_id, part_type, part_image_data, part_image_mime_type) VALUES (?, ?, ?, ?, ?)", 
                (story_id, post_id, 'image', part_image_data, part_image_mime_type)
        ).lastrowid
        db.commit()
        return inserted_id
    except Exception as e:
        print_except("insert_post_image_part",e)
        return False

def print_except(func, e):
        logging.exception(f"{func} Database error: {e}")
        logging.exception("Exception Type:", type(e).__name__)
        logging.exception("Exception Message:", str(e))