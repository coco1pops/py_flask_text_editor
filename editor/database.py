import sqlite3
import click
import os
import psycopg2
import logging

from flask import current_app, g

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

@click.command("init-db")
def init_db_command():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))

    click.echo("You successfully initialized the database!")

def get_db():
    if "db" not in g:
        try:
            if os.getenv("ENVIRONMENT") == "Production":

                g.db = psycopg2.connect(
                    dbname=current_app.config["DB_NAME"],
                    user=current_app.config["DB_USER"],
                    password=current_app.config["DB_PASSWORD"],
                    host=current_app.config["DB_HOST"],
                    port=current_app.config.get("DB_PORT", 5432)
                )

            else:    
                g.db = sqlite3.connect(
                    current_app.config["DATABASE"],
                    detect_types=sqlite3.PARSE_DECLTYPES,
                )
                g.db.row_factory = sqlite3.Row
        
        except Exception as e:
                logging.exception(f"An error occurred loading credentials: {e}")
                return False
    
    return g.db

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()