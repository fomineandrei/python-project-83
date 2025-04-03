import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def main_page():
    return "Любимая мамочка, я тебя очень сильно люблю." + \
        "Что хочешь на ужин в пятницу?)))"
