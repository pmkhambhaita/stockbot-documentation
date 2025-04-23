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
    
    def populate_random_data(self):
        """Fill the database with random quantities for each grid position"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Clear existing data
            cursor.execute('DELETE FROM items')
            # Generate data for each position
            for row in range(self.rows):
                for col in range(self.cols):
                    item_id = row * self.cols + col + 1  # 1-based index
                    quantity = random.randint(1, 10)
                    
                    cursor.execute('''
                        INSERT INTO items (ItemID, row, col, Quantity)
                        VALUES (?, ?, ?, ?)
                    ''', (item_id, row, col, quantity))
            
            conn.commit()
    
    def validate_item_id(self, item_id):
        """Validate if item_id exists and is within bounds"""
        max_id = self.rows * self.cols
        if not (1 <= item_id <= max_id):
            raise ValueError(f"ItemID must be between 1 and {max_id}")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM items WHERE ItemID = ?', (item_id,))
            if not cursor.fetchone():
                raise ValueError(f"ItemID {item_id} not found in database")
            return True
    
    def get_quantity(self, item_id):
        """Get quantity for a specific item"""
        self.validate_item_id(item_id)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT Quantity FROM items WHERE ItemID = ?', (item_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def update_quantity(self, item_id, new_quantity):
        """Update quantity for a specific item"""
        self.validate_item_id(item_id)
        if not isinstance(new_quantity, int):
            raise TypeError("Quantity must be an integer")
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative")
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE items 
                SET Quantity = ?
                WHERE ItemID = ?
            ''', (new_quantity, item_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_position(self, item_id):
        """Get grid position (row, col) for an item"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT row, col FROM items WHERE ItemID = ?', (item_id,))
            result = cursor.fetchone()
            return result if result else None

if __name__ == "__main__":
    try:
        # Initialise database with default dimensions
        db = InventoryDB(rows=10, cols=10)
        
        # Populate with random data
        db.populate_random_data()
        
        # Test: Print quantities for all positions
        print("Initial Database State:")
        for i in range(1, 101):  # 10x10 grid = 100 positions
            try:
                qty = db.get_quantity(i)
                pos = db.get_position(i)
                print(f"Position {i} (row={pos[0]}, col={pos[1]}): Quantity = {qty}")
            except Exception as e:
                print(f"Error reading position {i}: {e}")
                
        print("\nDatabase initialisation complete!")

        # Test: Update quantity for a specific item
        item_id_to_update = 50
        new_quantity = 20
        if db.update_quantity(item_id_to_update, new_quantity):
            print(f"\nQuantity for ItemID {item_id_to_update} updated to {new_quantity}")
        
        db.validate_item_id(101)  # Should raise an error
        
    except Exception as e:
        print(f"Error during database setup: {e}")