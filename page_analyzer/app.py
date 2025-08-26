import os

from dotenv import load_dotenv
from flask import Flask


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    from page_analyzer.views import index, not_found
    app.register_blueprint(index)
    app.register_error_handler(404, not_found)

    return app


app = create_app()


if __name__ == "__main__":
    app.run()
