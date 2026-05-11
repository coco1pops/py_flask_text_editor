CREATE TABLE users (
    user_id TEXT PRIMARY KEY CHECK (LENGTH(user_id) BETWEEN 4 AND 20),
    user_password TEXT,
    user_role TEXT NOT NULL CHECK (user_role IN ('Admin', 'Standard')),
    user_name);

/* New table for books */    
CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    author TEXT,
    description TEXT,
    user_id TEXT,
    temperature REAL, 
    top_p REAL, 
    seed INTEGER, 
    harassment_threshold TEXT, 
    hate_speech_threshold TEXT, 
    dangerous_content_threshold TEXT, 
    explicit_content_threshold TEXT, 
    model TEXT, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

/* New table for canon entries associated with books */
CREATE TABLE canon_entry(
    canon_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    entry_type TEXT NOT NULL CHECK (entry_type IN ('Relationship', 'Location', 'World Rule', 'Timeline', 'Other')),
    description TEXT,
    user_id TEXT, 
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

/* New table for characters associated with books */
CREATE TABLE book_chars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    char_id INTEGER NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (char_id) REFERENCES chars(char_id)
);

/* New table for chapters linking books and stories */
Create TABLE book_chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    story_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (story_id) REFERENCES stories(story_id)
);

CREATE TABLE stories (
    story_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    note TEXT,
    systeminstruction TEXT,
    newprompt,
    user_id TEXT, /* note forced to text */
    temperature REAL, 
    top_p REAL, 
    seed INTEGER, 
    harassment_threshold TEXT, 
    hate_speech_threshold TEXT, 
    dangerous_content_threshold TEXT, 
    explicit_content_threshold TEXT, 
    model TEXT, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    summary TEXT, /* New field for story summary */
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

/* New table for characters associated with stories */

CREATE TABLE story_chars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    char_id INTEGER NOT NULL,
    note TEXT,
    FOREIGN KEY (story_id) REFERENCES stories(story_id),
    FOREIGN KEY (char_id) REFERENCES chars(char_id)
);


CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    creator TEXT NOT NULL,
    multi_modal BOOLEAN DEFAULT false,
    message TEXT NOT NULL,
    FOREIGN KEY (story_id) REFERENCES stories(story_id)
);
CREATE TABLE post_parts (
    story_id INTEGER,
    post_id INTEGER,
    part_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    part_type TEXT NOT NULL CHECK (part_type IN ('text', 'image')),
    part_text TEXT,
    part_image_data BLOB,
    part_image_mime_type TEXT,
    FOREIGN KEY (post_id) REFERENCES posts(post_id)
);
CREATE TABLE chars (
    char_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    description TEXT,
    personality TEXT, 
    motivation TEXT,
    image_data BLOB, 
    image_mime_type TEXT,
    user_id,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE sysints (
    sysint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    description TEXT,
    instruction TEXT NOT NULL
);
CREATE TABLE params (id INTEGER PRIMARY KEY, temperature REAL, top_p REAL, seed INTEGER, hate_speech_threshold TEXT, dangerous_content_threshold TEXT, explicit_content_threshold TEXT, model TEXT, harassment_threshold);
CREATE VIEW unified_post_timeline AS
SELECT
    post_id,
    NULL AS part_id,	
    story_id,
    created,
    creator,
    multi_modal,
    message AS content,
    'post' AS source,
    NULL AS part_type,
    NULL AS part_text,
    NULL AS part_image_data,
    NULL AS part_image_mime_type
FROM posts

UNION ALL

SELECT
    post_id,
    part_id,
    story_id,
    created,
    NULL AS creator,
    'false' AS multi_modal,
    NULL AS content,
    'part' AS source,
    part_type,
    part_text,
    part_image_data,
    part_image_mime_type
FROM post_parts

ORDER BY post_id, created
/* unified_post_timeline(post_id,part_id,story_id,created,creator,multi_modal,content,source,part_type,part_text,part_image_data,part_image_mime_type) */;
