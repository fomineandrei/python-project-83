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

from page_analyzer.http import get_request
from page_analyzer.models import Urls, UrlsUrl

index = Blueprint('index', __name__, url_prefix='/')


@index.route('/')
def main_page():
    value = request.args.get('url')
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages, value=value)


@index.route('/urls', methods=["GET"])
def urls_get():
    messages = get_flashed_messages(with_categories=True)
    urls = Urls()
    
    sites = urls.all_urls

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

    url_in_db = Urls().find_by_url(domain)  
    
    if url_in_db.id:
        flash("Страница уже существует.", "alert alert-info")
        return redirect(url_for('index.url_info', id=url_in_db.id))
    return redirect(url_for('index.urls_add_new', domain=domain), 307)


@index.route('/urls/add', methods=["POST"])
def urls_add_new():
    domain = request.args.get('domain')
    
    new_url = Urls().add_new_url(domain)
    
    flash("Страница успешно добавлена.", "alert alert-success")
    return redirect(url_for("index.url_info", id=new_url.id))


@index.route('/urls/<id>', methods=['GET'])
def url_info(id):
    messages = get_flashed_messages(with_categories=True)

    url_in_db = Urls().find_by_id(id)
    
    if url_in_db.id:
        checks = UrlsUrl(url_id=id).url_checks
        return render_template("urls/url_check.html",
                            messages=messages,
                            url=url_in_db,
                            checks=checks)
    return render_template('404.html'), 404


@index.route('/urls/<id>/check', methods=['POST'])
def url_check(id):
    url = Urls().find_by_id(id)
    status_code = get_request(url.name)
    if not status_code:
        flash("Произошла ошибка при проверке", "alert alert-danger")
        redirect(url_for("index.url_info", id=url.id))
    new_check = UrlsUrl(url_id=url.id, status_code=status_code)
    new_check.save()
    return redirect(url_for("index.url_info", id=url.id))
    

@index.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
