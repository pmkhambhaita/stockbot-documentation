import sqlite3
import random

class InventoryDB:
    def __init__(self, rows=10, cols=10):
        """Initialise database with grid dimensions"""
        self.rows = rows
        self.cols = cols
        self.db_path = "inventory.db"
        # Create database and tables
        self._init_database()
    
    def _init_database(self):
        """Create the database and required tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Create items table with required fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    ItemID INTEGER PRIMARY KEY,
                    row INTEGER NOT NULL,
                    col INTEGER NOT NULL,
                    Quantity INTEGER NOT NULL,
                    UNIQUE(row, col)
                )
            ''')
            conn.commit()