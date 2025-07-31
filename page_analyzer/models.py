import datetime
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


class DBConnect():

    def __init__(self):
        self.conn = None

    def connect(self):
        load_dotenv()
        db_url = os.getenv("DATABASE_URL")
        try:
            self.conn = psycopg2.connect(db_url)
            return self.conn
        except Exception:
            raise Exception
        
    def sql_query(self, conn, query, **kwargs):
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute(query, kwargs)
            result = curs.fetchall()
        return result
        

class Urls(DBConnect):

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.created_at = kwargs.get('created_at')

    @property
    def all_urls(self):
        conn = self.connect()
        sql = """SELECT urls.id,
                    name,
                    CAST(MAX(url_checks.created_at) AS DATE) as last_check,
                    status_code
                FROM urls LEFT JOIN url_checks ON urls.id=url_checks.url_id
                GROUP BY urls.id, name, status_code
                ORDER BY urls.created_at DESC;"""
        result = self.sql_query(conn, sql)
        conn.close()
        urls = []
        for url_info in result:
            url = Urls(**url_info)
            url.last_check = url_info.get('last_check')
            url.status_code = url_info.get('status_code')
            urls.append(url)
        return urls

    def find_by_id(self, id):
        conn = self.connect()
        sql_find = """SELECT id, name, CAST(created_at AS DATE)
                    FROM urls WHERE id=%(id)s;"""
        sql_find_kwargs = {"id": id}
        result = self.sql_query(conn, sql_find, **sql_find_kwargs)
        conn.close()

        if result:
            check_result = result[0]
            self.created_at = check_result.get("created_at")
            self.id = check_result.get("id")
            self.url = check_result.get("name")
        return self
         
    def find_by_url(self, url):
        conn = self.connect()
        sql_check = 'SELECT * FROM urls WHERE name=%(url)s;'
        sql_check_kwargs = {"url": url}
        result = self.sql_query(conn, sql_check, **sql_check_kwargs)
        conn.close()
        
        if result:
            check_result = result[0]
            self.created_at = check_result.get("created_at")
            self.id = check_result.get("id")
            self.url = check_result.get("name")
        return self

    def add_new_url(self, url):
        conn = self.connect()
        sql = """INSERT INTO urls (name, created_at)
                VALUES (%(name)s, %(created_at)s) RETURNING id;"""
        self.created_at = datetime.datetime.now().replace(microsecond=0)
        self.url = url
        sql_args = {"name": self.url, "created_at": self.created_at}
        result = self.sql_query(conn, sql, **sql_args)
        self.id = result[0].get('id')
        conn.commit()
        conn.close()
        return self


class UrlsUrl(Urls):

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.url_id = kwargs.get("url_id")
        self.status_code = kwargs.get("status_code")
        self.h1 = kwargs.get("h1")
        self.title = kwargs.get("title")
        self.description = kwargs.get("description")
        self.created_at = kwargs.get("created_at")

    @property
    def url_checks(self):
        sql = """SELECT
                    id,
                    status_code,
                    h1,
                    title,
                    description,
                    CAST(created_at AS DATE)    
                FROM url_checks
                WHERE url_id=%(url_id)s"""
        sql_kwargs = {"url_id": self.url_id}
        conn = self.connect()
        result = self.sql_query(conn, sql, **sql_kwargs)
        checks = []
        for check_info in result:
            check = UrlsUrl(**check_info)
            checks.append(check)
        return checks

    def new_check(self, url_id):
        conn = self.connect()
        sql = """INSERT INTO url_checks (url_id, created_at)
                VALUES (%(url_id)s, %(created_at)s) RETURNING id;"""
        self.url_id = url_id
        self.created_at = datetime.datetime.now().replace(microsecond=0)
        sql_kwargs = {"url_id": self.url_id, "created_at": self.created_at}
        self.sql_query(conn, sql, **sql_kwargs)
        conn.commit()
        conn.close()
        return self