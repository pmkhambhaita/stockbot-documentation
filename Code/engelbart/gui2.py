# Import required libraries for GUI, file operations and system functions
import tkinter as tk
from tkinter import ttk  # Themed widgets for enhanced GUI appearance
import spa              # Custom module for pathfinding algorithms
import io              # For redirecting stdout to capture visualisation
import sys             # For system-level operations like stdout manipulation
import threading       # For multi-threading support
import queue           # For thread-safe data exchange
import config
import database

class GridVisualizer(tk.Toplevel):
    def __init__(self, parent, grid_rows, grid_cols, path=None, start=None, end=None, points=None, db=None):
        super().__init__(parent)
        self.title("Path Visualisation")
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.db = db  # Store database reference for stock checking
        
        # Track out-of-stock positions to keep them highlighted
        self.out_of_stock_positions = set()
        # Track user-selected points for stock level highlighting
        self.selected_points = set()
        
        # Calculate canvas size based on grid dimensions
        cell_size = 40
        canvas_width = grid_cols * cell_size + 1
        canvas_height = grid_rows * cell_size + 1
        
        # Create canvas for grid drawing
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack(padx=10, pady=10)
        
        # Store references for later use
        self.cell_size = cell_size
        self.path = path
        self.start = start
        self.end = end
        self.points = points
        
        # Draw the grid with numbers
        self.draw_grid()
        
        # Draw path and points if provided
        if path and start is not None and end is not None and points is not None and db is not None:
            self.visualize_path(path, start, end, points)
    
    def draw_grid(self):
        # Draw horizontal lines
        for i in range(self.grid_rows + 1):
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.grid_cols * self.cell_size, y, fill="gray")
        
        # Draw vertical lines
        for j in range(self.grid_cols + 1):
            x = j * self.cell_size
            self.canvas.create_line(x, 0, x, self.grid_rows * self.cell_size, fill="gray")
            
        # Add cell numbers
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                # Calculate position number (1-based)
                pos_num = spa.coordinates_to_index(row, col, self.grid_cols)
                
                # Calculate text position (center of cell)
                x = col * self.cell_size + self.cell_size // 2
                y = row * self.cell_size + self.cell_size // 2
                
                # Add text with improved font
                self.canvas.create_text(x, y, text=str(pos_num), font=("Arial", 10, "bold"))
    
    def visualise_path(self, path, start, end, points):
        # Update selected points for stock level highlighting
        self.selected_points = set()
        for x, y in points:
            self.selected_points.add((x, y))
            
            # Check if this point is out of stock and add to tracking set
            pos_num = spa.coordinates_to_index(x, y, self.grid_cols)
            quantity = self.db.get_quantity(pos_num)
            # Only add to out-of-stock if it was already at 0 before this run
            if quantity == 0:
                self.out_of_stock_positions.add((x, y))
        
        # First draw the path (lowest priority)
        for x, y in path:
            # Skip start, end, and intermediate points to avoid overwriting
            if (x, y) != start and (x, y) != end and (x, y) not in points:
                self.draw_cell(x, y, "#42f56f")  # Bright green for path
        
        # Draw intermediate points (medium priority)
        for point in points:
            pos_num = spa.coordinates_to_index(point[0], point[1], self.grid_cols)
            quantity = self.db.get_quantity(pos_num)
            
            if quantity == 0:
                # Check if it was already in out-of-stock before this run
                if (point[0], point[1]) in self.out_of_stock_positions:
                    # Was already out of stock - red
                    self.draw_cell(point[0], point[1], "#ff3333", True)  # Bright red
                else:
                    # Just became out of stock in this run - orange
                    self.draw_cell(point[0], point[1], "#ff9933", True)  # Bright orange
            elif quantity < 2:
                # Low stock - orange
                self.draw_cell(point[0], point[1], "#ff9933", True)  # Bright orange
            else:
                # Normal stock - yellow
                self.draw_cell(point[0], point[1], "#f5d742")  # Bright yellow
        
        # Draw start and end points (higher priority)
        self.draw_cell(start[0], start[1], "#4287f5")  # Bright blue for start
        self.draw_cell(end[0], end[1], "#4287f5")      # Bright blue for end
        
        # Draw any out-of-stock positions that aren't in the current path
        for x, y in self.out_of_stock_positions:
            if (x, y) not in self.selected_points and (x, y) != start and (x, y) != end:
                self.draw_cell(x, y, "#ff3333", True)  # Bright red
    
    def clear_visualisation(self):
        # Clear all colored cells but keep the grid and numbers
        self.canvas.delete("all")
        self.draw_grid()
        
        # Redraw only the out-of-stock positions
        if self.db:
            for x, y in self.out_of_stock_positions:
                self.draw_cell(x, y, "#ff3333", True)  # Bright red
        
        # Reset selected points but keep out-of-stock tracking
        self.selected_points = set()
        self.path = None
        self.start = None
        self.end = None
        self.points = None
    
    def draw_cell(self, row, col, color, is_stock_indicator=False):
        x1 = col * self.cell_size + 1
        y1 = row * self.cell_size + 1
        x2 = x1 + self.cell_size - 2
        y2 = y1 + self.cell_size - 2
        
        # Create rectangle with improved transparency to keep numbers visible
        rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        
        # Add the position number on top with contrasting color
        pos_num = spa.coordinates_to_index(row, col, self.grid_cols)
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        
        # Determine text color based on background brightness
        text_color = "black"
        if color in ["#4287f5", "#42f56f", "#ff3333", "#ff9933"]:  # For blue, green, red, orange backgrounds
            text_color = "white"
            
        # For stock indicators, add stock quantity if available
        if is_stock_indicator and self.db:
            quantity = self.db.get_quantity(pos_num)
            if quantity is not None:
                # Draw position number
                self.canvas.create_text(x, y - 7, text=str(pos_num), font=("Arial", 8, "bold"), fill=text_color)
                # Draw stock quantity
                self.canvas.create_text(x, y + 7, text=f"Stock: {quantity}", font=("Arial", 8), fill=text_color)
            else:
                self.canvas.create_text(x, y, text=str(pos_num), font=("Arial", 10, "bold"), fill=text_color)
        else:
            self.canvas.create_text(x, y, text=str(pos_num), font=("Arial", 10, "bold"), fill=text_color)

class PathfinderGUI:
    def __init__(self, root, rows=10, cols=10):  # Modified to accept dimensions
        # Store the root window and configure basic window properties
        self.root = root
        self.root.title("StockBot")
        self.root.geometry("800x600")  # Increased size to accommodate new layout
        
        # Initialize threading components
        self.processing = False
        self.result_queue = queue.Queue()
        
        # Configure grid weights to enable proper resizing
        self.root.grid_rowconfigure(2, weight=1)  # Output text area should expand
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create and configure the top frame for input elements
        input_frame = ttk.Frame(root)
        input_frame.grid(row=0, column=0, pady=10, padx=10, sticky='ew')
        input_frame.grid_columnconfigure(1, weight=1)  # Allow input field to expand
        
        # Create label and text entry field for points
        ttk.Label(input_frame, text="Enter points (space-separated):").grid(row=0, column=0, padx=(0, 10), sticky='w')
        self.point_entry = ttk.Entry(input_frame, width=50)
        self.point_entry.grid(row=0, column=1, sticky='ew')
        
        # Create row/column display frame
        dim_frame = ttk.Frame(root)
        dim_frame.grid(row=1, column=0, pady=5, padx=10, sticky='ew')
        
        # Row display
        ttk.Label(dim_frame, text="Rows:").grid(row=0, column=0, padx=(0, 5), sticky='w')
        row_var = tk.StringVar(value=str(rows))
        row_entry = ttk.Entry(dim_frame, textvariable=row_var, width=5, state='readonly')
        row_entry.grid(row=0, column=1, padx=(0, 20), sticky='w')
        
        # Column display
        ttk.Label(dim_frame, text="Columns:").grid(row=0, column=2, padx=(0, 5), sticky='w')
        col_var = tk.StringVar(value=str(cols))
        col_entry = ttk.Entry(dim_frame, textvariable=col_var, width=5, state='readonly')
        col_entry.grid(row=0, column=3, sticky='w')
        
        # Create legend frame
        legend_frame = ttk.LabelFrame(root, text="Legend:")
        legend_frame.grid(row=2, column=0, pady=10, padx=10, sticky='nw')
        
        # Add legend items
        ttk.Label(legend_frame, text="B", foreground="#4287f5", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(legend_frame, text="Start/End").grid(row=0, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(legend_frame, text="Y", foreground="#f5d742", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(legend_frame, text="User Points").grid(row=1, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(legend_frame, text="G", foreground="#42f56f", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(legend_frame, text="Path").grid(row=2, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(legend_frame, text="R", foreground="#ff3333", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(legend_frame, text="Out of Stock").grid(row=3, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(legend_frame, text="O", foreground="#ff9933", font=("Arial", 10, "bold")).grid(row=4, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(legend_frame, text="Low Stock (<2)").grid(row=4, column=1, padx=5, pady=2, sticky='w')
        
        # Create path distance display
        path_frame = ttk.Frame(root)
        path_frame.grid(row=3, column=0, pady=10, padx=10, sticky='w')
        
        ttk.Label(path_frame, text="Total path distance:").grid(row=0, column=0, padx=(0, 5), sticky='w')
        self.path_distance = ttk.Entry(path_frame, width=5, state='readonly')
        self.path_distance.grid(row=0, column=1, sticky='w')
        
        # Create main output area for displaying messages
        self.output_text = tk.Text(root, height=5, width=50)
        self.output_text.grid(row=4, column=0, pady=10, padx=10, sticky='nsew')
        
        # Create bottom frame for control buttons in a 2x2 grid
        button_frame = ttk.Frame(root)
        button_frame.grid(row=5, column=0, pady=10, padx=10, sticky='ew')
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Add buttons in a 2x2 grid
        query_button = ttk.Button(button_frame, text="Query Item Id", command=self.query_stock, width=20)
        query_button.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        
        obstacle_button = ttk.Button(button_frame, text="Obstacle mode", width=20)
        obstacle_button.grid(row=0, column=1, padx=10, pady=5, sticky='e')
        
        update_button = ttk.Button(button_frame, text="Update Quantity", command=self.update_stock, width=20)
        update_button.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        
        grid_button = ttk.Button(button_frame, text="Open grid visualisation", command=self.show_grid, width=20)
        grid_button.grid(row=1, column=1, padx=10, pady=5, sticky='e')
        
        # Add Find Path button separately
        find_path_button = ttk.Button(root, text="Find Path", command=self.find_path, width=20)
        find_path_button.grid(row=6, column=0, pady=10)
        
        # Initialise the pathfinding components with configured grid size
        self.grid = spa.Grid(rows, cols)
        self.path_finder = spa.PathFinder(self.grid)
        self.path_visualiser = spa.PathVisualiser(self.grid)
        
        # Initialize database with the same dimensions as the grid
        self.db = database.InventoryDB(rows, cols)
        self.db.populate_random_data()  # Initialize with random stock levels

    # Update find_path method to parse points directly from entry field
    def find_path(self):
        # Get and clean the input string from the entry field
        points_str = self.point_entry.get().strip()
        if not points_str:
            self.output_text.insert(tk.END, "Error: Please enter at least one position\n")
            return
            
        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Processing path...\n")
        
        # Split input by spaces
        import re
        point_list = re.split(r'[\s]+', points_str)
        
        # Process each point
        self.points = []  # Reset points list
        valid_input_points = []
        
        for point_str in point_list:
            if not point_str:  # Skip empty strings
                continue
                
            try:
                # Convert input string to single number
                index = int(point_str)
                
                # Validate index range
                if not (1 <= index <= self.grid.rows * self.grid.cols):
                    self.output_text.insert(tk.END, f"Error: Position {index} out of range (1-{self.grid.rows * self.grid.cols})\n")
                    continue
                
                # Check stock before adding point
                quantity = self.db.get_quantity(index)
                if quantity is None:
                    self.output_text.insert(tk.END, f"Error: Position {index} not found\n")
                    continue
                
                # Convert to coordinates (0-based)
                x, y = spa.index_to_coordinates(index, self.grid.cols)
                
                # Validate the point
                valid, error = spa.validate_point(x, y, self.grid.rows, self.grid.cols)
                if not valid:
                    self.output_text.insert(tk.END, f"Error: {error}\n")
                    continue
                
                # Add to valid input points
                valid_input_points.append((x, y, index, quantity))
                
            except ValueError:
                self.output_text.insert(tk.END, f"Error: '{point_str}' is not a valid number\n")
        
        # Check if we have any valid points
        if not valid_input_points:
            self.output_text.insert(tk.END, "Error: No valid positions entered\n")
            return
            
        # Process valid points for pathfinding
        try:
            # Define start and end points of the grid
            start_node = (0, 0)
            end_node = (self.grid.rows - 1, self.grid.cols - 1)
            
            # Inside find_path method, modify the section where we process valid points:
            # Filter out points with zero stock before pathfinding
            valid_points = []
            skipped_points = []
            
            for x, y, index, quantity in valid_input_points:
                if quantity > 0:
                    valid_points.append((x, y))
                    self.points.append((x, y))  # Add to class points list for visualisation
                else:
                    skipped_points.append((x, y, index))
                    # Add to out-of-stock tracking if visualisation window exists
                    if hasattr(self, 'viz_window') and self.viz_window and self.viz_window.winfo_exists():
                        # Only add to out-of-stock if it was already at 0 before this run
                        self.viz_window.out_of_stock_positions.add((x, y))
            
            if skipped_points:
                skipped_indices = [idx for _, _, idx in skipped_points]
                self.output_text.insert(tk.END, f"Skipping positions with no stock: {', '.join(map(str, skipped_indices))}\n")
            
            # If no valid points, find direct path from start to end
            if not valid_points:
                self.output_text.insert(tk.END, "No valid points with stock available. Finding direct path from start to end.\n")
                path = self.path_finder.find_path_through_points(start_node, [], end_node)
                valid_points = []  # Empty list for visualisation
            else:
                # Find path through all valid points
                path = self.path_finder.find_path_through_points(start_node, valid_points, end_node)
            
            if path:
                # Decrement stock for each valid intermediate point
                for x, y in valid_points:
                    item_id = spa.coordinates_to_index(x, y, self.grid.cols)
                    self.db.decrement_quantity(item_id)
                
                # Display path length
                path_length = len(path) - 1
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, f"Total path length: {path_length} steps\n")
                
                # Update path distance display
                path_distance_var = tk.StringVar(value=str(path_length))
                self.path_distance.config(textvariable=path_distance_var)
                
                # Convert path to position numbers
                path_indices = [spa.coordinates_to_index(x, y, self.grid.cols) 
                              for x, y in path]
                
                # Show path as position numbers
                path_str = " -> ".join([str(idx) for idx in path_indices])
                self.output_text.insert(tk.END, f"Path: {path_str}\n")
                
                # If visualisation window doesn't exist, create it
                if not hasattr(self, 'viz_window') or not self.viz_window or not self.viz_window.winfo_exists():
                    self.viz_window = GridVisualizer(
                        self.root, 
                        self.grid.rows, 
                        self.grid.cols, 
                        path=path, 
                        start=start_node, 
                        end=end_node, 
                        points=valid_points,
                        db=self.db
                    )
                else:
                    # If window exists, clear it and update with new path
                    self.viz_window.clear_visualisation()
                    self.viz_window.path = path
                    self.viz_window.start = start_node
                    self.viz_window.end = end_node
                    self.viz_window.points = valid_points
                    self.viz_window.db = self.db
                    self.viz_window.visualize_path(path, start_node, end_node, valid_points)
            else:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, "Error: No valid path found\n")
                
            # Clear points after finding path
            self.points = []
            
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error: {str(e)}\n")

    def clear_all(self):
        # Reset all components to initial state
        self.points = []
        self.point_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.path_distance.config(textvariable=tk.StringVar(value=""))
        self.output_text.insert(tk.END, "Cleared all points\n")
        
        # Clear visualisation but keep window open
        if hasattr(self, 'viz_window') and self.viz_window and self.viz_window.winfo_exists():
            self.viz_window.clear_visualisation()

    # Update query_stock and update_stock methods to work with the new interface
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
                    # Update visualisation if window exists
                    if hasattr(self, 'viz_window') and self.viz_window and self.viz_window.winfo_exists():
                        # Get coordinates from index
                        x, y = spa.index_to_coordinates(index, self.grid.cols)
                        
                        # Update out-of-stock tracking
                        if new_qty == 0:
                            self.viz_window.out_of_stock_positions.add((x, y))
                        else:
                            # Remove from out-of-stock if it was there
                            self.viz_window.out_of_stock_positions.discard((x, y))
                        
                        # Refresh visualisation if path exists
                        if self.viz_window.path:
                            self.viz_window.clear_visualisation()
                            self.viz_window.visualize_path(
                                self.viz_window.path,
                                self.viz_window.start,
                                self.viz_window.end,
                                self.viz_window.points
                            )
                        else:
                            # Just refresh the grid with out-of-stock items
                            self.viz_window.clear_visualisation()
                    
                    popup.destroy()
                except ValueError:
                    self.output_text.insert(tk.END, "Error: Please enter a valid number\n")
                except Exception as e:
                    self.output_text.insert(tk.END, f"Error: {str(e)}\n")
            
            ttk.Button(popup, text="Update", command=do_update).pack(pady=5)
            
        except ValueError:
            self.output_text.insert(tk.END, "Error: Please enter a valid position number\n")

    def show_grid(self):
        # Create or show visualisation window
        if not hasattr(self, 'viz_window') or not self.viz_window or not self.viz_window.winfo_exists():
            self.viz_window = GridVisualizer(
                self.root, 
                self.grid.rows, 
                self.grid.cols,
                db=self.db  # Pass database reference
            )
        else:
            # If window exists but is minimized, restore it
            self.viz_window.deiconify()
            self.viz_window.lift()

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