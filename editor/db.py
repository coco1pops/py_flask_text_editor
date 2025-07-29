from editor.database import get_db

def get_characters():
    db = get_db()
    try:
        rows = db.execute("SELECT char_id, name from characters").fetchall()
        return rows
    except Exception as e:
        print_except("get_characters",e)
        return False

def get_character(char_id):
    db = get_db()
    try:         
        row = db.execute("SELECT char_id, name, description, personality, motivation, image_data, image_mime_type from characters WHERE char_id = (?)", (char_id)).fetchone()
        return row
    except Exception as e:
        print_except("get_character",e)
        return False
    
def insert_character(name, description, personality, motivation, image_id, image_mime_type):      
    db=get_db()
    try:
        row_id=db.execute(f"INSERT INTO characters (name, description, personality, motivation, image_id, image_mime_type) VALUES (?, ?, ?, ?, ?, ?)", 
                   (name, description, personality, motivation, image_id, image_mime_type,)).lastrowid
        db.commit()
        return row_id
    except Exception as e:
        print_except("get_character",e)
        return False   

def update_character(char_id, field, value):
    db=get_db()
    try:
        db.execute(f"UPDATE characters SET ({field} = (?) WHERE char_id = (?)", (value, char_id))
        db.commit()
        return True
    except Exception as e:
        print_except("get_character",e)
        return False

def delete_character(char_id):
    db=get_db()
    try:
        db.execute(f"DELETE from characters WHERE char_id = (?)", (char_id))
        db.commit()
        return True
    except Exception as e:
        print_except("get_character",e)
        return False

def print_except(func, e):
        print(f"{func} Error generating content: {e}")
        print("Exception Type:", type(e).__name__)
        print("Exception Message:", str(e))