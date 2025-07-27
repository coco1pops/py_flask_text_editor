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
    isdirty BOOLEAN DEFAULT false,
    message TEXT NOT NULL,
    FOREIGN KEY (story_id) REFERENCES stories(story_id)
        ON DELETE CASCADE
);
