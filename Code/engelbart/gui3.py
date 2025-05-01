# Import required libraries for GUI, file operations and system functions
import tkinter as tk
from tkinter import ttk  # Themed widgets for enhanced GUI appearance
import spa              # Custom module for pathfinding algorithms
import io               # For redirecting stdout to capture visualisation
import sys              # For system-level operations like stdout manipulation
import threading        # For multi-threading support
import queue            # For thread-safe data exchange
import config
import database

class PathfinderGUI:
    def __init__(self, root, rows=10, cols=10):
        # Store the root window and configure basic window properties
        self.root = root
        # ... # self.root.title("StockBot")
        self.root.geometry("600x500")  # Adjusted size for cleaner layout

        # Initialise threading components
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
        ttk.Label(input_frame, text="Enter points:").grid(row=0, column=0, padx=(0, 10), sticky='w')
        self.point_entry = ttk.Entry(input_frame, width=50)
        self.point_entry.grid(row=0, column=1, sticky='ew')

        # Create legend frame
        legend_frame = ttk.LabelFrame(root, text="Legend:")
        legend_frame.grid(row=1, column=0, pady=5, padx=10, sticky='nw')

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

        # Create main output area for displaying messages
        self.output_text = tk.Text(root, height=5, width=50)
        self.output_text.grid(row=2, column=0, pady=10, padx=10, sticky='nsew')

        # Create bottom frame for control buttons in a 2x2 grid
        button_frame = ttk.Frame(root)
        button_frame.grid(row=3, column=0, pady=10, padx=10, sticky='ew')
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
        find_path_button.grid(row=4, column=0, pady=10)

        # Initialise the pathfinding components with configured grid size
        self.grid = spa.Grid(rows, cols)
        self.path_finder = spa.PathFinder(self.grid)
        self.path_visualiser = spa.PathVisualiser(self.grid)

        # Initialise database with the same dimensions as the grid
        self.db = database.InventoryDB(rows, cols)
        self.db.populate_random_data()  # Initialise with random stock levels

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

                # Convert path to position numbers
                path_indices = [spa.coordinates_to_index(x, y, self.grid.cols)
                              for x, y in path]

                # Show path as position numbers
                path_str = " -> ".join([str(idx) for idx in path_indices])
                self.output_text.insert(tk.END, f"Path: {path_str}\n")

                # If visualisation window doesn't exist, create it
                if not hasattr(self, 'viz_window') or not self.viz_window or not self.viz_window.winfo_exists():
                    self.viz_window = GridVisualiser(
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
                    self.viz_window.visualise_path(path, start_node, end_node, valid_points)

                # Clear points after finding path
                self.points = []

            else:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, "Error: No valid path found\n")

        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error: {str(e)}\n")

    def clear_all(self):
        # Reset all components to initial state
        self.points = []
        self.point_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        # self.path_distance display removed
        self.output_text.insert(tk.END, "Cleared all points\n")

        # Clear visualisation but keep window open
        if hasattr(self, 'viz_window') and self.viz_window and self.viz_window.winfo_exists():
            self.viz_window.clear_visualisation()

    def query_stock(self):
        # Create popup for position input
        popup = tk.Toplevel(self.root)
        popup.title("Query Stock")
        popup.geometry("200x100")

        ttk.Label(popup, text="Enter position number:").pack(pady=5)
        pos_entry = ttk.Entry(popup)
        pos_entry.pack(pady=5)

        def do_query():
            try:
                index = int(pos_entry.get())
                quantity = self.db.get_quantity(index)

                if quantity is not None:
                    pos = self.db.get_position(index)
                    self.output_text.insert(tk.END, f"Position {index} (row={pos[0]}, col={pos[1]}): Stock = {quantity}\n")
                else:
                    self.output_text.insert(tk.END, f"Position {index} not found\n")
                popup.destroy()

            except ValueError:
                self.output_text.insert(tk.END, "Error: Please enter a valid number\n")
                popup.destroy()

        ttk.Button(popup, text="Query", command=do_query).pack(pady=5)

    def update_stock(self):
        # Create popup for position input
        pos_popup = tk.Toplevel(self.root)
        pos_popup.title("Update Stock")
        pos_popup.geometry("200x100")

        ttk.Label(pos_popup, text="Enter position number:").pack(pady=5)
        pos_entry = ttk.Entry(pos_popup)
        pos_entry.pack(pady=5)

        def get_quantity():
            try:
                index = int(pos_entry.get())
                pos_popup.destroy()

                # Create second popup for quantity input
                qty_popup = tk.Toplevel(self.root)
                qty_popup.title("Update Stock")
                qty_popup.geometry("200x100")

                ttk.Label(qty_popup, text="Enter new quantity:").pack(pady=5)
                qty_entry = ttk.Entry(qty_popup)
                qty_entry.pack(pady=5)

                def do_update():
                    try:
                        new_qty = int(qty_entry.get())
                        self.db.update_quantity(index, new_qty)
                        self.output_text.insert(tk.END, f"Updated stock for position {index} to {new_qty}\n")

                        # Update visualisation if window exists
                        if hasattr(self, 'viz_window') and self.viz_window and self.viz_window.winfo_exists():
                            x, y = spa.index_to_coordinates(index, self.grid.cols)

                            if new_qty == 0:
                                self.viz_window.out_of_stock_positions.add((x, y))
                            else:
                                self.viz_window.out_of_stock_positions.discard((x, y))

                            # Refresh visualisation, potentially redrawing the path
                            if self.viz_window.path:
                                self.viz_window.clear_visualisation()
                                self.viz_window.visualise_path(
                                    self.viz_window.path,
                                    self.viz_window.start,
                                    self.viz_window.end,
                                    self.viz_window.points
                                )
                            else:
                                self.viz_window.clear_visualisation()

                        qty_popup.destroy()
                    except ValueError:
                        self.output_text.insert(tk.END, "Error: Please enter a valid number\n")
                        qty_popup.destroy()

                ttk.Button(qty_popup, text="Update", command=do_update).pack(pady=5)

            except ValueError:
                self.output_text.insert(tk.END, "Error: Please enter a valid position number\n")
                pos_popup.destroy()

        ttk.Button(pos_popup, text="Next", command=get_quantity).pack(pady=5)