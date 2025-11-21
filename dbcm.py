"""
Name: Noah Pagtakhan
Date: 2025-11-14
Description:
    Database context manager for the DBOperations class
"""

import sqlite3

class DBCM:
    """Database context manager which establishes a connection to the database"""
    def __init__(self, db_name):
        """initializing db_name and setting connection and cursor variable"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """enter method setting the connection to the database"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        return self.cursor
    """returns cursor and not the connection"""
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """If there is an error, call a rollback to its most recent and stable version"""
        if exc_type is not None:
            self.conn.rollback()
        else:
            """If there are no errors, commit all changes"""
            self.conn.commit()

        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()