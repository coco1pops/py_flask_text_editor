from editor.database import get_db
import base64

def get_characters():
    db = get_db()
    try:
        rows = db.execute("SELECT char_id, created, name, description from chars").fetchall()
        return rows
    except Exception as e:
        print_except("get_characters",e)
        return False

def get_character(char_id):
    db = get_db()
    try:         
        row = db.execute("SELECT char_id, name, description, personality, motivation, image_data, image_mime_type from chars WHERE char_id = (?)", 
                         (char_id,)).fetchone()
        
        image_data = None

        if row['image_mime_type'] != "":
            image_data ="data:" + row['image_mime_type'] + ";base64," + base64.b64encode(row['image_data']).decode('utf-8')
        
        format_row=({"char_id" : row['char_id'],"name": row['name'],"description": row['description'], "personality" : row['personality'], "motivation" : row['motivation'],
                           "image_data" : image_data, "image_mime_type" : row['image_mime_type']})

        return format_row
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

def print_except(func, e):
        print(f"{func} Error generating content: {e}")
        print("Exception Type:", type(e).__name__)
        print("Exception Message:", str(e))