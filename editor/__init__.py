import os
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

from editor.models import database
from editor.models import chat_service

load_dotenv()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limit to 2MB
    app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
    app.secret_key = app.config["SECRET_KEY"]

    if app.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    env_value = os.getenv("ENVIRONMENT")
    if env_value and env_value.strip() == "PROD":
        logging.info (f"Startup-DB Credentials: Name {app.config['DB_NAME']} User {app.config['DB_USER']} Password {app.config['DB_PASSWORD']}")
    else:
        logging.info (f"Startup-DB Credentials {app.config['DATABASE']}")

    logging.info("Startup-Initialising database")
    database.init_app(app)
    logging.info("Startup-Initialising chat")
    chat_service.initialize_global_chat_service();
    
    logging.info("Startup-Initialising login module")
    login_manager.init_app(app)
    login_manager.login_view="login.login"
    from .models import auth 
    from editor.routes import login, pages, parameters, stories
    
    logging.info("Startup-registering blueprints")
    app.register_blueprint(login.bp)
    app.register_blueprint(pages.bp)
    app.register_blueprint(stories.bp)
    app.register_blueprint(parameters.bp)

    return app

# This conditional ensures that 'app' is only created when the module is run directly by Gunicorn
if __name__ != '__main__':
    app = create_app()

