import os

from dotenv import load_dotenv
from flask import Flask


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    from page_analyzer.views import index
    app.register_blueprint(index)

    return app


app = create_app()
