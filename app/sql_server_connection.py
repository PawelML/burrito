import pyodbc
import os
from dotenv import load_dotenv

class SQLServerConnection:
    def __init__(self):
        load_dotenv()
        self.server = os.getenv('SQL_SERVER')
        self.database = os.getenv('SQL_DATABASE')
        self.username = os.getenv('SQL_USERNAME')
        self.password = os.getenv('SQL_PASSWORD')
        self.driver = os.getenv('SQL_DRIVER')
        
    def get_connection(self) -> pyodbc.Connection:
        """Create and return a connection to SQL Server"""
        conn_str = f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
        return pyodbc.connect(conn_str)


