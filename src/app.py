from flask import Flask
from controllers.home_controller import home_blueprint
from controllers.about_controller import about_blueprint
from controllers.chat_controller import chat_blueprint
from middleware.error_handler import register_exception_handlers
from utils.app_config import AppConfig

# Initialize main Flask server using default static and template locations:
server = Flask(__name__)

# Enable working with server-side sessions:
server.secret_key = AppConfig.server_side_session_secret_key

# Register exception handlers:
register_exception_handlers(server)

# Register blueprints:
server.register_blueprint(home_blueprint)
server.register_blueprint(about_blueprint)
server.register_blueprint(chat_blueprint)