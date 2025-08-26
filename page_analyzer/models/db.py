import datetime
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


class DataBase:
    
    def get_connection(self):
        db_url = os.getenv("DATABASE_URL")
        return psycopg2.connect(db_url)
    
    def connection_commit(self, conn):
        conn.commit()

    def connection_close(self, conn):
        conn.close()

    def get_urls(self, conn):
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
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute(query)
            result = curs.fetchall()
        return result
        
    def find_url_by_id(self, conn, id):
        query = """
            SELECT 
                id,
                name,
                CAST(created_at AS DATE)
            FROM urls
            WHERE id=%(id)s;"""
        query_kwargs = {'id': id}
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute(query, query_kwargs)
            result = curs.fetchone()
        return result
    
    def find_url_by_name(self, conn, name):
        query = """
            SELECT 
                id,
                name,
                CAST(created_at AS DATE)
            FROM urls
            WHERE name=%(name)s;"""
        query_kwargs = {'name': name}
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute(query, query_kwargs)
            result = curs.fetchone()
        return result

    def save_url(self, conn, url):
        query = """
            INSERT INTO urls (name, created_at)
            VALUES (%(name)s, %(created_at)s) RETURNING id;"""
        query_kwargs = {
            'name': url,
            'created_at': datetime.datetime.now()
        }
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute(query, query_kwargs)
            id = curs.fetchone()
        return id | query_kwargs

    def get_url_checks(self, conn, url_id):
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
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute(query, query_kwargs)
            result = curs.fetchall()
        return result
    
    def check_save(self, conn, check):
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
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute(query, query_kwargs)
            id = curs.fetchone()
        return id | query_kwargs
