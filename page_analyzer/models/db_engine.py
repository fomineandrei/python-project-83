import os

from dotenv import load_dotenv

from page_analyzer.models.db import DataBase
from tests.test_data.db_test import DataBaseTest

load_dotenv()


def current_db():
    test_env = os.getenv("TEST")
    if test_env == "True":
        db = DataBaseTest()
    else:
        db = DataBase()
    
    def wrapper():
        return db
    
    return wrapper


db_engine = current_db()