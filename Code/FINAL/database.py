import sqlite3
import random
import logging

# Get the main logger
logger = logging.getLogger(__name__)

class InventoryDB:
    def __init__(self, rows, cols):
        """Initialize database with grid dimensions"""
        self.rows = rows
        self.cols = cols
        self.db_path = "inventory.db"
        logger.info(f"Initializing database with dimensions {rows}x{cols}")
        self._init_database()
    
    def _init_database(self):
        """Create the database and required tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
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
                logger.info("Database table created successfully")
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            raise
    
    def populate_random_data(self):
        """Fill the database with random quantities for each grid position"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM items')
                logger.info("Cleared existing inventory data")
                
                for row in range(self.rows):
                    for col in range(self.cols):
                        item_id = row * self.cols + col + 1
                        quantity = random.randint(1, 10)
                        cursor.execute('''
                            INSERT INTO items (ItemID, row, col, Quantity)
                            VALUES (?, ?, ?, ?)
                        ''', (item_id, row, col, quantity))
                conn.commit()
                logger.info(f"Populated database with random data for {self.rows*self.cols} positions")
        except Exception as e:
            logger.error(f"Error populating database: {str(e)}")
            raise
    
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
        try:
            self.validate_item_id(item_id)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT Quantity FROM items WHERE ItemID = ?', (item_id,))
                result = cursor.fetchone()
                quantity = result[0] if result else None
                logger.debug(f"Retrieved quantity {quantity} for ItemID {item_id}")
                return quantity
        except Exception as e:
            logger.error(f"Error getting quantity for ItemID {item_id}: {str(e)}")
            raise

    def update_quantity(self, item_id, new_quantity):
        """Update quantity for a specific item"""
        try:
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
                logger.info(f"Updated quantity to {new_quantity} for ItemID {item_id}")
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating quantity for ItemID {item_id}: {str(e)}")
            raise

    def decrement_quantity(self, item_id):
        """Decrement quantity by 1 for a specific item"""
        try:
            self.validate_item_id(item_id)
            current_qty = self.get_quantity(item_id)
            if current_qty is None or current_qty <= 0:
                logger.warning(f"Cannot decrement: ItemID {item_id} has no stock")
                return False
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE items 
                    SET Quantity = Quantity - 1
                    WHERE ItemID = ? AND Quantity > 0
                ''', (item_id,))
                conn.commit()
                logger.info(f"Decremented quantity for ItemID {item_id}")
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error decrementing quantity for ItemID {item_id}: {str(e)}")
            raise

    def get_position(self, item_id):
        """Get grid position (row, col) for an item"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT row, col FROM items WHERE ItemID = ?', (item_id,))
            result = cursor.fetchone()
            return result if result else None

if __name__ == "__main__":
    try:
        # Initialize database using config dimensions
        db = InventoryDB()
        
        # Populate with random data
        db.populate_random_data()
        
        # Test: Print quantities for all positions
        print("Initial Database State:")
        total_positions = db.rows * db.cols
        for i in range(1, total_positions + 1):
            try:
                qty = db.get_quantity(i)
                pos = db.get_position(i)
                print(f"Position {i} (row={pos[0]}, col={pos[1]}): Quantity = {qty}")
            except Exception as e:
                print(f"Error reading position {i}: {e}")
                
        print("\nDatabase initialization complete!")
        
    except Exception as e:
        print(f"Error during database setup: {e}")