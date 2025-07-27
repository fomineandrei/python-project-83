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
        self.url = kwargs.get('url')
        self.created_at = kwargs.get('created_at')

    @property
    def all_urls(self):
        conn = self.connect()
        sql = """SELECT urls.id, name, check_date, status_code
                FROM urls LEFT JOIN url_check ON urls.id=url_check.url_id
                ORDER BY created_at DESC;"""
        result = self.sql_query(conn, sql)
        conn.close()
        urls_in_db = [Urls(id=el.get('id'), url=el.get('name'),
                           created_at=el.get('created_at')) for el in result]
        return urls_in_db

    def find_url_by_id(self, id):
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
            return True
        return False
         
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
            return True
        return False

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
