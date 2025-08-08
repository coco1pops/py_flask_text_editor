PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS stories;

CREATE TABLE stories (
    story_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    note TEXT,
    systemInstruction TEXT,
    author TEXT NOT NULL,
    newprompt
);

DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    creator TEXT NOT NULL,
    multi_modal BOOLEAN DEFAULT false,
    message TEXT NOT NULL,
    FOREIGN KEY (story_id) REFERENCES stories(story_id)
        ON DELETE CASCADE
);

DROP TABLE IF EXISTS chars;

CREATE TABLE chars (
    char_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    description TEXT,
    personality TEXT, 
    motivation TEXT,
    image_data BLOB, 
    image_mime_type TEXT
);

DROP TABLE IF EXISTS post_parts;

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

CREATE VIEW unified_post_timeline AS
SELECT
    post_id,
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

ORDER BY post_id, created;


