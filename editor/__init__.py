import os
from dotenv import load_dotenv
from flask import Flask

from editor import pages, database, stories, chat_service, parameters

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limit to 2MB
    app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']


    database.init_app(app)
    chat_service.initialize_global_chat_service();
    
    app.register_blueprint(pages.bp)
    app.register_blueprint(stories.bp)
    app.register_blueprint(parameters.bp)

    print(f"Current Environment: {os.getenv('ENVIRONMENT')}")
    print(f"Using Database: {app.config.get('DATABASE')}")
    return app
