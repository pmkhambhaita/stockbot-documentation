# Import required libraries
# tkinter for GUI components
import tkinter as tk
from tkinter import ttk
# Custom pathfinding module
import spasb1 as spa
# io and sys for redirecting stdout to capture visualisation output
import io
import sys

class PathfinderGUI:
    """
    Main GUI class that handles the warehouse pathfinding visualisation.
    Provides an interface for users to input points and visualise paths.
    """
    def __init__(self, root):
        # Initialize main window properties
        self.root = root
        self.root.title("StockBot")
        # Set window size - 600x400 provides enough space for visualisation
        self.root.geometry("600x400")
        # Configure grid weights to allow proper resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create input frame for point entry
        # Frame is needed to group the entry field and add button
        input_frame = ttk.Frame(root)
        input_frame.grid(row=0, column=0, pady=10, padx=10, sticky='ew')
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Entry field for coordinates
        # Uses grid layout for responsive design
        self.point_entry = ttk.Entry(input_frame)
        self.point_entry.grid(row=0, column=0, padx=(0, 10), sticky='ew')
        
        # Button to add points to the path
        add_button = ttk.Button(input_frame, text="Add Point", command=self.add_point)
        add_button.grid(row=0, column=1)
        
        # Text area for displaying the path visualisation
        # Height and width set for optimal visualisation of 10x10 grid
        self.output_text = tk.Text(root, height=15, width=50)
        self.output_text.grid(row=1, column=0, pady=10, padx=10, sticky='nsew')
        
        # Frame for control buttons at bottom
        button_frame = ttk.Frame(root)
        button_frame.grid(row=2, column=0, pady=5)
        
        # Path finding and clear buttons
        start_button = ttk.Button(button_frame, text="Find Path", command=self.find_path)
        start_button.grid(row=0, column=0, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_all)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Initialize backend components
        # 10x10 grid size chosen for clear visualisation
        self.grid = spa.Grid(10, 10)
        self.path_finder = spa.PathFinder(self.grid)
        self.path_visualiser = spa.PathVisualiser(self.grid)
        
        # List to store intermediate points
        self.points = []

    def add_point(self):
        """
        Validates and adds a point to the path.
        Handles coordinate parsing and boundary checking.
        """
        point_str = self.point_entry.get().strip()
        try:
            # Parse x,y coordinates, removing parentheses and spaces
            # Validation needed to ensure proper coordinate format
            x, y = map(int, point_str.strip('()').replace(' ', '').split(','))
            
            # Validate coordinates are within grid boundaries
            if 0 <= x < self.grid.rows and 0 <= y < self.grid.cols:
                self.points.append((x, y))
                self.point_entry.delete(0, tk.END)
                self.output_text.insert(tk.END, f"Added point: ({x}, {y})\n")
            else:
                # Log warning if coordinates are out of bounds
                spa.logger.warning(f"Coordinates ({x},{y}) out of bounds")
        except ValueError:
            # Log error if input format is invalid
            spa.logger.error("Invalid input format. Please use 'x,y' format")

    def find_path(self):
        """
        Finds and visualises path through all added points.
        Uses stdout redirection to capture visualisation output.
        """
        if not self.points:
            spa.logger.warning("No points added")
            return

        # Fixed start and end points at opposite corners
        start_node = (0, 0)
        end_node = (self.grid.rows - 1, self.grid.cols - 1)
        
        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        path = self.path_finder.find_path_through_points(start_node, self.points, end_node)
        
        if path:
            # Redirect stdout to capture visualisation
            old_stdout = sys.stdout
            result = io.StringIO()
            sys.stdout = result
            
            self.path_visualiser.visualise_path(path, start_node, end_node, self.points)
            
            # Restore stdout and display visualisation
            sys.stdout = old_stdout
            visualisation = result.getvalue()
            
            self.output_text.insert(tk.END, visualisation)
        else:
            self.output_text.insert(tk.END, "No valid path found\n")

    def clear_all(self):
        """
        Resets the application state by clearing all points and output.
        """
        self.points = []
        self.point_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Cleared all points\n")

def main():
    root = tk.Tk()
    PathfinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()