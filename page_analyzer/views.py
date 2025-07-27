from urllib.parse import urlparse

import validators
from flask import (
    Blueprint,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.models import Urls

index = Blueprint('index', __name__, url_prefix='/')


@index.route('/')
def main_page():
    value = request.args.get('url')
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages, value=value)


@index.route('/urls', methods=["GET"])
def urls_get():
    urls = Urls()
    sites = urls.all_urls
    messages = get_flashed_messages(with_categories=True)
    return render_template('urls/index.html',
                           sites=sites,
                           messages=messages)


@index.route('/urls', methods=["POST"])
def urls_post():
    url = request.form.get('url')
    if validators.url(url) is not True:
        flash("Некорректный URL", "alert alert-danger")
        return redirect(url_for('index.main_page', url=url))
    
    domain = urlparse(url). \
        _replace(path='', params='', query='', fragment='').geturl()
    
    url_obj = Urls()
    
    url_in_db = url_obj.find_by_url(domain)
    if url_in_db:
        flash("Страница уже существует.", "alert alert-info")
        return redirect(url_for('index.url_info', id=url_obj.id))
    return redirect(url_for('index.urls_add_new', domain=domain), 307)


@index.route('/urls/add', methods=["POST"])
def urls_add_new():
    domain = request.args.get('domain')
    new_url = Urls()
    new_url.add_new_url(domain)
    flash("Страница успешно добавлена.", "alert alert-success")
    return redirect(url_for("index.url_info", id=new_url.id))


@index.route('/urls/<id>', methods=['GET'])
def url_info(id):
    messages = get_flashed_messages(with_categories=True)
    url = Urls()
    check_by_id = url.find_url_by_id(id)
    checks = {}
    if check_by_id:
        return render_template("urls/url_check.html",
                            messages=messages,
                            url=url,
                            checks=checks)
    return render_template('404.html'), 404
    

@index.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@index.route('/urls/<id>/check', methods=['POST'])
def url_check(id):
    return {}