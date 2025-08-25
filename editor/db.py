from editor.database import get_db
import base64
import markdown
import logging
import os

from werkzeug.security import generate_password_hash
from flask_login import current_user
#
# Character database functions
#
def get_characters():
    db = get_db()
    try:
        sep=build_sel()
        select = f"SELECT char_id, created, name, description from chars WHERE user_id = {sep}"
        rows = db.execute(select, (current_user.id,)).fetchall()
        return rows
    except Exception as e:
        print_except("get_characters",e)
        return False

def get_character(char_id, allow_not_found=False):
    
    try:         
        row = get_character_raw(char_id)
        
        if not row and not allow_not_found:
            print_except("get_character","Record not found")

        image_data = None

        if row['image_mime_type'] != "" and row['image_mime_type'] != None:
            image_data ="data:" + row['image_mime_type'] + ";base64," + base64.b64encode(row['image_data']).decode('utf-8')
        
        format_row=({"char_id" : row['char_id'],"name": row['name'],"description": row['description'], "personality" : row['personality'], "motivation" : row['motivation'],
                           "image_data" : image_data, "image_mime_type" : row['image_mime_type']})

        return format_row
    except Exception as e:
        print_except("get_character",e)
    
def get_character_raw(char_id, allow_not_found=False):
    db = get_db()
    sep=build_sel()
    select=f"SELECT char_id, name, description, personality, motivation, image_data, image_mime_type from chars WHERE char_id = {sep}"
    select=add_user(select)
    try:
        row = db.execute(select, 
            (char_id, current_user.id)).fetchone()
        if not row and not allow_not_found:
            print_except("get_character_raw","Record not found")
        return row
    except Exception as e:
        print_except("get_character_raw",e)

def insert_character(name, description, personality, motivation):      
    db=get_db()
    try:
        sep=build_sel()
        ins=f"INSERT INTO chars (name, description, personality, motivation, user_id) VALUES ({sep}, {sep}, {sep}, {sep}, {sep})"
        if os.getenv("ENVIRONMENT")=="PROD":
            ins=f"{ins} RETURNING char_id"
            cursor=db.execute(ins,(name, description, personality, motivation, current_user.id ))
            row_id=cursor.fetchone()["char_id"]                  
        else:
            row_id=db.execute(ins, 
                       (name, description, personality, motivation, current_user.id)).lastrowid
        db.commit()
        return row_id
    except Exception as e:
        print_except("insert_character",e)

def update_character(char_id, field, value):
    db=get_db()
    try:
        sep=build_sel()
        upd=f"UPDATE chars SET ({field} = {sep}) WHERE char_id = {sep}"
        upd=add_user(upd)
        db.execute(upd, (value, char_id, current_user.id,))
        db.commit()
        return True
    except Exception as e:
        print_except("update_character",e)
    
def update_all_character(char_id, name, description, personality, motivation):
    db=get_db()
    sep=build_sel()
    upd=f"UPDATE chars SET name = {sep}, description = {sep}, personality = {sep}, motivation = {sep} WHERE char_id = {sep}"
    upd=add_user(upd)
    try:
        db.execute(upd, 
                   (name, description, personality, motivation, char_id, current_user.id))
        db.commit()
        return True
    except Exception as e:
        print_except("update_all_character",e)

def update_character_image(char_id, image_data, image_mime_type):
    db=get_db()
    try:
        sep=build_sel()
        upd=f"UPDATE chars SET image_data = {sep}, image_mime_type = {sep} WHERE char_id = {sep}"
        upd=add_user(upd)
        db.execute(upd, 
                   (image_data, image_mime_type, char_id, current_user.id))
        db.commit()
        return True
    except Exception as e:
        print_except("update_image_character",e)

def delete_character(char_id):
    db=get_db()
    try:
        sep=build_sel()
        exc=f"DELETE from chars WHERE char_id = {sep}"
        db.execute(exc, (char_id,))
        db.commit()
        return True
    except Exception as e:
        print_except("delete_character",e)

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

def get_story(story_id, allow_not_found=False):
    try:
        db = get_db()
        sep = build_sel()
        select = f"SELECT story_id, title, note, systeminstruction, created FROM stories WHERE story_id = {sep}"
        select=add_user(select)
        story = db.execute(select
            , (story_id,current_user.id,)
            ).fetchone()
        
        if not story and not allow_not_found:
            print_except("get_story","Record not found")

        return story
    except Exception as e:
        print_except("get_story",e)
    
def get_latest_story():
    try:
        db = get_db()
        sep=build_sel()
        select = f"SELECT story_id, title, note FROM stories WHERE created = (SELECT MAX(created) from stories WHERE user_id = {sep})"
        story = db.execute (select,(current_user.id,)).fetchone()
        return story
    except Exception as e:
        print_except("get_latest_story", e)
    
def insert_story(title, note, systeminstruction):
    try:
        db = get_db()
        sep = build_sel()
        ins=f"INSERT INTO stories (title, note, systeminstruction, user_id) VALUES ({sep}, {sep} ,{sep}, {sep})"
        if os.getenv("ENVIRONMENT")=="PROD":
            ins=f"{ins} RETURNING story_id"
            cursor=db.execute(ins,(title, note, systeminstruction,current_user.id,))
            story_id=cursor.fetchone()["story_id"]
        else:       
            story_id = db.execute(ins,(title, note, systeminstruction,current_user.id,)).lastrowid
        db.commit()
        return story_id
    except Exception as e:
        print_except("insert_story",e)
    
def get_stories():
    try:
        db = get_db()
        sep=build_sel()
        select = f"SELECT story_id, title, note, created FROM stories WHERE user_id = {sep} ORDER BY created DESC"
        stories = db.execute(select, (current_user.id,)).fetchall()
        return stories
    except Exception as e:
        print_except("get_stories",e)
    
def delete_story(story_id):
    try:
        db = get_db()
        sep = build_sel()

        exc=f"DELETE FROM post_parts WHERE story_id={sep}"
        db.execute(exc, (story_id,))

        exc=f"DELETE FROM posts WHERE story_id={sep}"
        db.execute(exc, (story_id,))

        exc=f"DELETE FROM stories WHERE story_id={sep}"
        db.execute(exc,(story_id,))
        db.commit()

    except Exception as e:
        print_except("delete_story",e)

def update_story(story_id, field, value):
    db=get_db()
    sep = build_sel()
    try:
        upd = f"UPDATE stories SET {field} = {sep} WHERE story_id = {sep}"
        upd = add_user(upd)
        db.execute(upd, (value, story_id, current_user.id,))
        db.commit()
        return True
    except Exception as e:
        print_except("update_story",e)
    
#
# Posts database functions
#

def get_message(post_id, allow_not_found=False):
    db=get_db()
    sep=build_sel()
    try:
        select=f"SELECT message FROM posts WHERE post_id = {sep}"
        row = db.execute(select, (post_id,)).fetchone()
        if not row and not allow_not_found:
            print_except("get_message", "Record not found")
        return row['message']

    except Exception as e:
        print_except("get_message",e)
    
def update_message(post_id, value):
    db=get_db()
    sep=build_sel()
    try:
        upd = f"UPDATE posts SET message = {sep} WHERE post_id = {sep}"
        db.execute(upd, (value, post_id,))
        db.commit()
        return True
    
    except Exception as e:
        print_except("update_message",e)

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

def get_all_posts_raw(story_id):
    try:
        db = get_db()
        sep=build_sel()
        select_string = "SELECT post_id, created, creator, multi_modal, content, source, part_type, part_text, part_image_data, part_image_mime_type"
        select_string = f"{select_string} from unified_post_timeline WHERE story_id={sep} ORDER BY post_id, created ASC"
        posts = db.execute(select_string,(story_id,)).fetchall()
    
        return posts

    except Exception as e:
        print_except("get_all_posts_raw",e)

def delete_posts_from(story_id, post_id):
    try:
        db = get_db()
        sep = build_sel()
        exc=f"DELETE FROM post_parts WHERE story_id={sep} AND post_id >={sep}"
        db.execute(exc, (story_id, post_id))  

        exc=f"DELETE FROM posts WHERE story_id={sep} AND post_id >= {sep}"
        db.execute(exc, (story_id,post_id,))

        db.commit()
    except Exception as e:
        print_except("delete_posts_from",e)

def insert_post(story_id, creator, prompt, multi):
    try:
        db=get_db()
        sep=build_sel()
        ins=f"INSERT INTO posts (story_id, creator, message, multi_modal) VALUES ({sep}, {sep}, {sep}, {sep})"
        if os.getenv("ENVIRONMENT")=="PROD":
            ins=f"{ins} RETURNING post_id"
            cursor=db.execute(ins,(story_id, creator, prompt, multi, ))
            inserted_id=cursor.fetchone()["post_id"]                  
        else:
            inserted_id=db.execute(ins, (story_id, creator, prompt, multi)).lastrowid
        db.commit()
        return inserted_id
    except Exception as e:
        print_except("insert_post",e)

#
# Database functions for post parts
#
def insert_post_text_part(story_id, post_id, part_text):
    try:
        db=get_db()
        sep=build_sel()
        ins=f"INSERT INTO post_parts (story_id, post_id, part_type, part_text) VALUES ({sep}, {sep}, 'text', {sep})"
        if os.getenv("ENVIRONMENT")=="PROD":
            ins=f"{ins} RETURNING part_id"
            cursor=db.execute(ins,(story_id, post_id, part_text, ))
            inserted_id=cursor.fetchone()["part_id"]
        else:  
            inserted_id=db.execute(ins, (story_id, post_id, part_text)).lastrowid
        
        db.commit()
        return inserted_id
    
    except Exception as e:
        print_except("insert_post_text_part",e)
    
def insert_post_image_part(story_id, post_id, part_image_data, part_image_mime_type):
    try:
        db=get_db()
        sep=build_sel()
        ins=f"INSERT INTO post_parts (story_id, post_id, part_type, part_image_data, part_image_mime_type) VALUES ({sep}, {sep}, 'image', {sep}, {sep})"
        if os.getenv("ENVIRONMENT")=="PROD":
            ins=f"{ins} RETURNING part_id"
            cursor=db.execute(ins,(story_id, post_id, part_image_data, part_image_mime_type,))
            inserted_id=cursor.fetchone()["part_id"]
        else:  
            inserted_id=db.execute(ins,(story_id, post_id, part_image_data, part_image_mime_type)).lastrowid
        db.commit()
        return inserted_id

    except Exception as e:
        print_except("insert_post_image_part",e)
#
# Database functions for users
#    
def get_user(user_id, allow_not_found=False):
    db=get_db()
    sep=build_sel()
    select=f"SELECT user_id, user_password, user_name, user_role FROM USERS WHERE user_id = {sep}"
    try:
        usr=db.execute(select,(user_id,)).fetchone()
        if not usr and not allow_not_found:
            print_except("get_user", "Record not found")
        return usr
    except Exception as e:
        print_except("get_user",e)

def get_users():
    db=get_db()
    select=f"SELECT user_id, user_password, user_name, user_role FROM USERS"
    try:
        return db.execute(select).fetchall()
    except Exception as e:
        print_except("get_user",e)

def insert_user(user_id, user_password, user_name, user_role):
    db=get_db()
    sep=build_sel()
    hash_password = generate_password_hash(user_password)

    ins=f"INSERT INTO users (user_id, user_password, user_name, user_role) VALUES ({sep}, {sep}, {sep}, {sep})"
    try:
        db.execute(ins,(user_id, hash_password, user_name, user_role))
        db.commit()
        return user_id
    except Exception as e:
        print_except("insert_user",e)

def insert_base_user():
    try:
        row=get_user("john",allow_not_found=True)
        if not row:
            insert_user("john", "supauser", "John Admin Role", "Admin")
    except Exception as e:
        print_except("insert_base_user", e)

def update_user(user_id, user_name, user_role):
    db=get_db()
    sep=build_sel()
  
    try:
        upd=f"UPDATE users SET user_name ={sep}, user_role = {sep} WHERE user_id = {sep}"
        db.execute(upd,(user_name, user_role, user_id,))
        db.commit()
        return True
    except Exception as e:
        print_except("update_user",e)

def user_reset_pass(user_id, new_password):
    db=get_db()
    sep=build_sel()
    hash_password = generate_password_hash(new_password)

    try:
        upd=f"UPDATE users SET user_password ={sep} WHERE user_id = {sep}"
        db.execute(upd,(hash_password, user_id,))
        db.commit()
        return True
    except Exception as e:
        print_except("user_reset_pass",e)

def delete_user(user_id):
    db=get_db()
    sep=build_sel()
    exc=f"DELETE FROM USERS WHERE user_id = {sep}"
    try:
        db.execute(exc,(user_id,))
        db.commit()
        return True
    except Exception as e:
        print_except("delete_user",e)
#
# Database functions for sysints
#    
def get_sysint(sysint_id, allow_not_found=False):
    db=get_db()
    sep=build_sel()
    select=f"SELECT sysint_id, name, created, description, instruction FROM sysints WHERE sysint_id = {sep}"
    try:
        usr=db.execute(select,(sysint_id,)).fetchone()
        if not usr and not allow_not_found:
            print_except("get_sysint", "Record not found")
        return usr
    except Exception as e:
        print_except("get_sysint",e)

def get_sysints():
    db=get_db()
    select=f"SELECT sysint_id, name, created, description, instruction FROM sysints"
    try:
        return db.execute(select).fetchall()
    except Exception as e:
        print_except("get_sysints",e)

def insert_sysint(name, description, instruction):
    db=get_db()
    sep=build_sel()
    ins=f"INSERT INTO sysints (name, description, instruction) VALUES ({sep}, {sep}, {sep})"
    try:
        if os.getenv("ENVIRONMENT")=="PROD":
            ins=f"{ins} RETURNING sysint_id"
            cursor=db.execute(ins,(name, description, instruction))
            inserted_id=cursor.fetchone()["sysint_id"]
        else:  
            inserted_id=db.execute(ins,(name, description, instruction)).lastrowid
        db.commit()
        return inserted_id
    except Exception as e:
        print_except("insert_sysint",e)

def update_sysint(sysint_id, name, description, instruction):
    db=get_db()
    sep=build_sel()
  
    try:
        upd=f"UPDATE sysints SET name ={sep}, description = {sep}, instruction = {sep} WHERE sysint_id = {sep}"
        db.execute(upd,(name, description, instruction, sysint_id,))
        db.commit()
        return True
    except Exception as e:
        print_except("update_user",e)

def delete_sysint(sysint_id):
    db=get_db()
    sep=build_sel()
    exc=f"DELETE FROM sysints WHERE sysint_id = {sep}"
    try:
        db.execute(exc,(sysint_id,))
        db.commit()
        return True
    except Exception as e:
        print_except("delete_sysint",e)

# 
# Database functions utilities
#
def print_except(func, e):
        logging.exception(f"{func} Database error: {e}")
        logging.exception("Exception Type:", type(e).__name__)
        #logging.exception("Exception Message:", str(e))
        if isinstance(e,str):
            mess=e;
        else:
            mess=e.args[0]
        raise Exception(f"Error in {func}, {mess} ")

def build_sel()->str:
    if os.getenv("ENVIRONMENT") == "PROD":
        return "%s"
    else:
        return "?"

def add_user(sql)->str:
    sep=build_sel()
    sql=f"{sql} AND user_id = {sep}"
    return sql