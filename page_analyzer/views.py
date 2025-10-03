from urllib.parse import urlparse

import validators
from flask import (
    Blueprint,
    flash,
    get_flashed_messages,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.http import get_http_response
from page_analyzer.models.db import db_engine
from page_analyzer.models.models import Url, UrlCheck

index = Blueprint('index', __name__, url_prefix='/')


db = db_engine()


@index.route('/')
def main_page():
    value = request.args.get('url')
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages, value=value)


@index.route('/urls', methods=["GET"])
def urls_get():
    messages = get_flashed_messages(with_categories=True)

    connection = db.get_connection()
    urls = db.get_urls(connection)
    sites = [Url(**url) for url in urls]
    db.connection_close(connection)

    return render_template('urls/index.html',
                           sites=sites,
                           messages=messages)


@index.route('/urls', methods=["POST"])
def urls_post():
    url = request.form.get('url')
    if validators.url(url) is not True:
        flash("Некорректный URL", "alert alert-danger")
        response = make_response(render_template('index.html'))
        response.status_code = 422
        return redirect(url_for('index.main_page', url=url), response)
    
    domain = urlparse(url). \
        _replace(path='', params='', query='', fragment='').geturl()
    
    connection = db.get_connection()
    url_in_db = db.find_url_by_name(connection, domain)
    db.connection_close(connection)
    
    if url_in_db:
        url = Url(**url_in_db)
        flash("Страница уже существует.", "alert alert-info")
        return redirect(url_for('index.url_info', id=url.id))
    
    return redirect(url_for('index.urls_add_new', domain=domain), 307)


@index.route('/urls/add', methods=["POST"])
def urls_add_new():
    domain = request.args.get('domain')
    
    connection = db.get_connection()
    saved_url = db.save_url(connection, domain)
    new_url = Url(**saved_url)
    db.connection_commit(connection)
    db.connection_close(connection)
    
    flash("Страница успешно добавлена.", "alert alert-success")
    return redirect(url_for("index.url_info", id=new_url.id))


@index.route('/urls/<id>', methods=['GET'])
def url_info(id):
    messages = get_flashed_messages(with_categories=True)

    connection = db.get_connection()
    url_in_db = db.find_url_by_id(connection, id)
    url = Url(**url_in_db)
    
    if url.id:
        checks_in_db = db.get_url_checks(connection, url.id)
        checks = [UrlCheck(**check) for check in checks_in_db]
        db.connection_close(connection)
        return render_template("urls/url_check.html",
                            messages=messages,
                            url=url,
                            checks=checks)
    db.connection_close(connection)
    return render_template('404.html'), 404


@index.route('/urls/<id>/check', methods=['POST'])
def url_check(id):
    connection = db.get_connection()
    url_in_db = db.find_url_by_id(connection, id)
    url = Url(**url_in_db)
    http_response = get_http_response(url.name)
    if not http_response.get('status_code'):
        flash("Произошла ошибка при проверке", "alert alert-danger")
        return redirect(url_for("index.url_info", id=url.id))
    
    url_info = UrlCheck(url_id=url.id, **http_response)
    db.check_save(connection, url_info)
    db.connection_commit(connection)
    db.connection_close(connection)
    flash("Страница успешно проверена", "alert alert-success")
    return redirect(url_for("index.url_info", id=url_info.url_id))
    

@index.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
