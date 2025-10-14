import datetime
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


class DBConnection:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.conn = psycopg2.connect(
            self.database_url,
            cursor_factory=RealDictCursor
        )

    def __enter__(self):
        with self.conn as conn:
            return conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()


class Urls:
    def __init__(self):
        self.cursor = DBConnection()

    def get_urls(self):
        query = """
            SELECT
                urls.id AS id,
                urls.name AS name,
                CAST(last_checks.created_at AS DATE) AS last_check,
                last_checks.status_code AS status_code
            FROM  urls
            LEFT JOIN (
                SELECT
                    max_checks.url_id AS url_id,
                    max_checks.created_at AS created_at,
                    checks.status_code AS status_code
                FROM (SELECT
                        url_id,
                        MAX(created_at) AS created_at
                    FROM url_checks
                    GROUP BY url_id) AS max_checks
                INNER JOIN url_checks AS checks ON
                    max_checks.url_id=checks.url_id
                WHERE max_checks.created_at=checks.created_at) AS last_checks ON
                urls.id=last_checks.url_id
            ORDER BY urls.created_at DESC;"""
        with self.cursor as curs:
            curs.execute(query)
            result = curs.fetchall()
        return result
        
    def find_url_by_id(self, id):
        query = """
            SELECT 
                id,
                name,
                CAST(created_at AS DATE)
            FROM urls
            WHERE id=%(id)s;"""
        query_kwargs = {'id': id}
        with self.cursor as curs:
            curs.execute(query, query_kwargs)
            result = curs.fetchone()
        return result
    
    def find_url_by_name(self, name):
        query = """
            SELECT 
                id,
                name,
                CAST(created_at AS DATE)
            FROM urls
            WHERE name=%(name)s;"""
        query_kwargs = {'name': name}
        with self.cursor as curs:
            curs.execute(query, query_kwargs)
            result = curs.fetchone()
        return result

    def save_url(self, url):
        query = """
            INSERT INTO urls (name, created_at)
            VALUES (%(name)s, %(created_at)s) RETURNING id;"""
        query_kwargs = {
            'name': url,
            'created_at': datetime.datetime.now()
        }
        with self.cursor as curs:
            curs.execute(query, query_kwargs)
            id = curs.fetchone()
        return id | query_kwargs

    def get_url_checks(self, url_id):
        query = """SELECT
                    id,
                    status_code,
                    h1,
                    title,
                    description,
                    CAST(created_at AS DATE)   
                FROM url_checks
                WHERE url_id=%(url_id)s
                ORDER BY url_checks.created_at DESC"""
        query_kwargs = {"url_id": url_id}
        with self.cursor as curs:
            curs.execute(query, query_kwargs)
            result = curs.fetchall()
        return result
    
    def check_save(self, check):
        query = """
            INSERT INTO url_checks (url_id, created_at, status_code,
                h1, title, description)
            VALUES (%(url_id)s, %(created_at)s, %(status_code)s,
                %(h1)s, %(title)s, %(description)s) RETURNING id;"""
        query_kwargs = {
            'url_id': check.url_id,
            'status_code': check.status_code,
            'h1': check.h1,
            'title': check.title,
            'description': check.description,
            'created_at': datetime.datetime.now()
        }
        with self.cursor as curs:
            curs.execute(query, query_kwargs)
            id = curs.fetchone()
        return id | query_kwargs
