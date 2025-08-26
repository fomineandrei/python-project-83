from page_analyzer.models.db import DataBase


class DataBaseTest(DataBase):
    def __init__(self):
        self.connection = super().get_connection()

    def get_connection(self):
        return self.connection

    def connection_commit(self, conn):
        pass
    
    def connection_close(self, conn):
        pass

    