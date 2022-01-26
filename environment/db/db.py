import os
import sqlite3
from functions import PARENT_DIR


local_db = os.path.join(PARENT_DIR, "db", "venv-sql.db")

class SQL():
    def __init__(self, venv_db: str = local_db) -> None:
        self.connection = sqlite3.connect(venv_db)
        self.cursor = self.connection.cursor()

    def go(self,
           query: str = '',
           is_file: bool = False,
           argument_list: list = []) -> list:
        if is_file:
            with open(query, 'r') as query_file_io:
                query = query_file_io.read()
        self.cursor.execute(query, *argument_list)
        result_set = self.cursor.fetchall()
        return result_set
