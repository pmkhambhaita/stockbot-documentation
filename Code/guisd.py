# Import required libraries for GUI, file operations and system functions
import tkinter as tk
from tkinter import ttk  # Themed widgets for enhanced GUI appearance
import spa              # Custom module for pathfinding algorithms
import queue           # For thread-safe data exchange
import config
import database

class GridVisualizer(tk.Toplevel):
    def __init__(self, parent, grid_rows, grid_cols, path=None, start=None, end=None, points=None):
        super().__init__(parent)
        self.title("Path Visualization")
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        
        # Calculate canvas size based on grid dimensions
        cell_size = 40
        canvas_width = grid_cols * cell_size + 1
        canvas_height = grid_rows * cell_size + 1
        
        # Create canvas for grid drawing
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack(padx=10, pady=10)
        
        # Draw the grid
        self.cell_size = cell_size
        self.draw_grid()
        
        # Draw path and points if provided
        if path and start is not None and end is not None and points is not None:
            self.visualize_path(path, start, end, points)
    
    def draw_grid(self):
        # Draw horizontal lines
        for i in range(self.grid_rows + 1):
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.grid_cols * self.cell_size, y, fill="black")
        
        # Draw vertical lines
        for j in range(self.grid_cols + 1):
            x = j * self.cell_size
            self.canvas.create_line(x, 0, x, self.grid_rows * self.cell_size, fill="black")
    
    def visualize_path(self, path, start, end, points):
        # Draw start and end points (light blue)
        self.draw_cell(start[0], start[1], "light blue")
        self.draw_cell(end[0], end[1], "light blue")
        
        # Draw intermediate points (yellow)
        for point in points:
            self.draw_cell(point[0], point[1], "yellow")
        
        # Draw path (green)
        for x, y in path:
            # Skip start, end, and intermediate points to avoid overwriting
            if (x, y) != start and (x, y) != end and (x, y) not in points:
                self.draw_cell(x, y, "green")
    
    def draw_cell(self, row, col, color):
        x1 = col * self.cell_size
        y1 = row * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

class PathfinderGUI:
    def __init__(self, root, rows=10, cols=10):  # Modified to accept dimensions
        # Store the root window and configure basic window properties
        self.root = root
        self.root.title("StockBot")
        self.root.geometry("600x400")
        
        # Initialize threading components
        self.processing = False
        self.result_queue = queue.Queue()
        
        # Configure grid weights to enable proper resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create and configure the top frame for input elements
        input_frame = ttk.Frame(root)
        input_frame.grid(row=0, column=0, pady=10, padx=10, sticky='ew')
        input_frame.grid_columnconfigure(0, weight=1)  # Allow input field to expand
        
        # Create text entry field for coordinates
        self.point_entry = ttk.Entry(input_frame)
        self.point_entry.grid(row=0, column=0, padx=(0, 10), sticky='ew')
        
        # Add range label after point entry
        self.range_label = ttk.Label(input_frame, text=f"Enter position (1-{rows*cols})")
        self.range_label.grid(row=1, column=0, columnspan=2, pady=(5,0))
        
        # Create button to add points to the path
        add_button = ttk.Button(input_frame, text="Add Point", command=self.add_point)
        add_button.grid(row=0, column=1)
        
        # Create main output area for displaying messages (smaller now)
        self.output_text = tk.Text(root, height=5, width=50)
        self.output_text.grid(row=1, column=0, pady=10, padx=10, sticky='nsew')
        
        # Create bottom frame for control buttons
        button_frame = ttk.Frame(root)
        button_frame.grid(row=2, column=0, pady=5)
        
        # Add buttons for path finding and clearing
        start_button = ttk.Button(button_frame, text="Find Path", command=self.find_path)
        start_button.grid(row=0, column=0, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_all)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Initialise the pathfinding components with configured grid size
        self.grid = spa.Grid(rows, cols)
        self.path_finder = spa.PathFinder(self.grid)
        self.path_visualiser = spa.PathVisualiser(self.grid)
        
        # Initialise empty list to store intermediate points
        self.points = []

        # Initialize database with the same dimensions as the grid
        self.db = database.InventoryDB(rows, cols)
        self.db.populate_random_data()  # Initialize with random stock levels
        
        # Create stock management frame
        stock_frame = ttk.Frame(root)
        stock_frame.grid(row=3, column=0, pady=5)
        
        # Add stock management buttons
        query_button = ttk.Button(stock_frame, text="Query Stock", command=self.query_stock)
        query_button.grid(row=0, column=0, padx=5)
        
        update_button = ttk.Button(stock_frame, text="Update Stock", command=self.update_stock)
        update_button.grid(row=0, column=1, padx=5)

    def add_point(self):
        # Get and clean the input string from the entry field
        point_str = self.point_entry.get().strip()
        try:
            # Convert input string to single number
            index = int(point_str)
            
            # Validate index range
            if not (1 <= index <= self.grid.rows * self.grid.cols):
                self.output_text.insert(tk.END, f"Error: Position {index} out of range (1-{self.grid.rows * self.grid.cols})\n")
                return
            
            # Check stock before adding point
            quantity = self.db.get_quantity(index)
            if quantity is None:
                self.output_text.insert(tk.END, f"Error: Position {index} not found\n")
                return
            if quantity <= 0:
                self.output_text.insert(tk.END, f"Warning: Skipping position {index} - Out of stock\n")
                return
            
            # Convert to coordinates (0-based)
            x, y = spa.index_to_coordinates(index, self.grid.cols)
            
            # Validate the point
            valid, error = spa.validate_point(x, y, self.grid.rows, self.grid.cols)
            if not valid:
                self.output_text.insert(tk.END, f"Error: {error}\n")
                return
            
            self.points.append((x, y))
            self.point_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added position {index} (Stock: {quantity})\n")
            
        except ValueError:
            self.output_text.insert(tk.END, "Error: Please enter a valid number\n")

    def find_path(self):
        # Check if there are any points to process
        if not self.points:
            self.output_text.insert(tk.END, "Error: No intermediate points added. Please add at least one point.\n")
            return
    
        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Processing path...\n")
        
        try:
            # Define start and end points of the grid
            start_node = (0, 0)
            end_node = (self.grid.rows - 1, self.grid.cols - 1)
            
            # Find path through all points
            path = self.path_finder.find_path_through_points(start_node, self.points, end_node)
            
            if path:
                # Decrement stock for each intermediate point
                for x, y in self.points:
                    item_id = spa.coordinates_to_index(x, y, self.grid.cols)
                    self.db.decrement_quantity(item_id)
                
                # Display path length
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, f"Total path length: {len(path) - 1} steps\n")
                
                # Convert path to position numbers
                path_indices = [spa.coordinates_to_index(x, y, self.grid.cols) 
                              for x, y in path]
                
                # Show path as position numbers
                path_str = " -> ".join([str(idx) for idx in path_indices])
                self.output_text.insert(tk.END, f"Path: {path_str}\n")
                
                # Close previous visualization window if it exists
                if hasattr(self, 'viz_window') and self.viz_window and self.viz_window.winfo_exists():
                    self.viz_window.destroy()
                
                # Create visualization window
                self.viz_window = GridVisualizer(
                    self.root, 
                    self.grid.rows, 
                    self.grid.cols, 
                    path=path, 
                    start=start_node, 
                    end=end_node, 
                    points=self.points
                )
            else:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, "Error: No valid path found through all points\n")
        
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error: {str(e)}\n")

    def clear_all(self):
        # Reset all components to initial state
        self.points = []
        self.point_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Cleared all points\n")
        
        # Close visualization window if it exists
        if hasattr(self, 'viz_window') and self.viz_window and self.viz_window.winfo_exists():
            self.viz_window.destroy()
            self.viz_window = None

    def query_stock(self):
        try:
            point_str = self.point_entry.get().strip()
            if not point_str:
                self.output_text.insert(tk.END, "Please enter a position to query\n")
                return
                
            index = int(point_str)
            quantity = self.db.get_quantity(index)
            
            if quantity is not None:
                pos = self.db.get_position(index)
                self.output_text.insert(tk.END, f"Position {index} (row={pos[0]}, col={pos[1]}): Stock = {quantity}\n")
            else:
                self.output_text.insert(tk.END, f"Position {index} not found\n")
                
        except ValueError:
            self.output_text.insert(tk.END, "Error: Please enter a valid number\n")

    def update_stock(self):
        try:
            point_str = self.point_entry.get().strip()
            if not point_str:
                self.output_text.insert(tk.END, "Please enter a position to update\n")
                return
                
            index = int(point_str)
            
            # Create popup for quantity input
            popup = tk.Toplevel(self.root)
            popup.title("Update Stock")
            popup.geometry("200x100")
            
            ttk.Label(popup, text="Enter new quantity:").pack(pady=5)
            qty_entry = ttk.Entry(popup)
            qty_entry.pack(pady=5)
            
            def do_update():
                try:
                    new_qty = int(qty_entry.get())
                    self.db.update_quantity(index, new_qty)
                    self.output_text.insert(tk.END, f"Updated stock for position {index} to {new_qty}\n")
                    popup.destroy()
                except ValueError:
                    self.output_text.insert(tk.END, "Error: Please enter a valid number\n")
                except Exception as e:
                    self.output_text.insert(tk.END, f"Error: {str(e)}\n")
            
            ttk.Button(popup, text="Update", command=do_update).pack(pady=5)
            
        except ValueError:
            self.output_text.insert(tk.END, "Error: Please enter a valid position number\n")

def main():
    # Get grid dimensions from config window (will only show once)
    rows, cols = config.get_grid_config()
    if rows is None or cols is None:
        return  # User closed the config window
        
    # Create and start the main application window
    root = tk.Tk()
    app = PathfinderGUI(root, rows, cols)
    root.mainloop()

if __name__ == "__main__":
    main()