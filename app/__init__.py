import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    app.config["OPENWEATHER_API_KEY"] = os.getenv("OPENWEATHER_API_KEY", "")

    from .routes import main
    app.register_blueprint(main)

    return app
