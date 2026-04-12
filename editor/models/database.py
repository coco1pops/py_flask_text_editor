
import logging
import os
# Successfully installed flask-sqlalchemy-3.1.1 greenlet-3.4.0 sqlalchemy-2.0.49

from flask_sqlalchemy import SQLAlchemy
from flask import current_app

db = SQLAlchemy()

def init_app(app):
    # Configure DB URL based on environment
    env_value = os.getenv("ENVIRONMENT")

    if env_value and env_value.strip() == "PROD":
        logging.debug("DB - Loading Postgres database")

        instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")
        socket_dir = "/cloudsql"
        host = f"{socket_dir}/{instance_connection_name}"

        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"postgresql+psycopg://{app.config['DB_USER']}:"
            f"{app.config['DB_PASSWORD']}@/{app.config['DB_NAME']}?host={host}"
        )
    else:
        logging.debug(f"DB - Loading SQLite database {app.config['DATABASE']}")
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"sqlite:///{app.config['DATABASE']}"
        )
        logging.debug(f"DB - SQLite database path: {os.path.abspath(app.config['DATABASE'])}")


    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        logging.debug(f"DB - Engine URL: {db.engine.url}")


def print_except(func, e):
    logging.exception(f"{func} Database error: {e}")
    logging.exception("Exception Type:", {type(e).__name__})

    if isinstance(e,str):
        mess=e;
    else:
        mess=str(e)
    raise Exception(f"Error in {func}, {mess} ") from e