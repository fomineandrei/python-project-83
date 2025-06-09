from flask import Blueprint, render_template

index = Blueprint('index', __name__, url_prefix='/')


@index.route('/', methods=["GET", "POST"])
def main_page():
    return render_template('index.html')