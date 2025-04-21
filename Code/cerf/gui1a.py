# Import required libraries for GUI, file operations and system functions
import tkinter as tk
from tkinter import ttk  # Themed widgets for enhanced GUI appearance
import spa              # Custom module for pathfinding algorithms
import io              # For redirecting stdout to capture visualisation
import sys             # For system-level operations like stdout manipulation
import threading       # For multi-threading support
import queue           # For thread-safe data exchange

class PathfinderGUI:
    def __init__(self, root):
        # Store the root window and configure basic window properties
        self.root = root
        self.root.title("StockBot")
        self.root.geometry("600x400")  # Set initial window dimensions
        
        # Initialise threading components
        self.processing = False  # Flag to check if a pathfinding operation is in progress
        self.result_queue = queue.Queue()  # Queue to hold results and transfer safely
        
        # Configure grid weights to enable proper resising
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create and configure the top frame for input elements
        input_frame = ttk.Frame(root)
        input_frame.grid(row=0, column=0, pady=10, padx=10, sticky='ew')
        input_frame.grid_columnconfigure(0, weight=1)  # Allow input field to expand
        
        # Create text entry field for coordinates
        self.point_entry = ttk.Entry(input_frame)
        self.point_entry.grid(row=0, column=0, padx=(0, 10), sticky='ew')
        
        # Create button to add points to the path
        add_button = ttk.Button(input_frame, text="Add Point", command=self.add_point)
        add_button.grid(row=0, column=1)
        
        # Create main output area for displaying the path and messages
        self.output_text = tk.Text(root, height=15, width=50)
        self.output_text.grid(row=1, column=0, pady=10, padx=10, sticky='nsew')
        
        # Create bottom frame for control buttons
        button_frame = ttk.Frame(root)
        button_frame.grid(row=2, column=0, pady=5)
        
        # Add buttons for path finding and clearing
        start_button = ttk.Button(button_frame, text="Find Path", command=self.find_path)
        start_button.grid(row=0, column=0, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_all)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Initialise the pathfinding components with a 10x10 grid
        self.grid = spa.Grid(10, 10)
        self.path_finder = spa.PathFinder(self.grid)
        self.path_visualiser = spa.PathVisualiser(self.grid)
        
        # Initialise empty list to store intermediate points
        self.points = []

    def add_point(self):
        # Get and clean the input string from the entry field
        point_str = self.point_entry.get().strip()
        try:
            # Convert input string to x,y coordinates
            x, y = map(int, point_str.strip('()').replace(' ', '').split(','))
            
            # Validate the point using centralised validation function
            valid, error = spa.validate_point(x, y, self.grid.rows, self.grid.cols)
            if not valid:
                self.output_text.insert(tk.END, f"Error: {error}\n")
                return
            
            # Add valid point to the list and clear input field
            self.points.append((x, y))
            self.point_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added point: ({x}, {y})\n")
            
        except ValueError:
            # Handle invalid input format
            self.output_text.insert(tk.END, "Error: Invalid format. Please use 'x,y' format (e.g., '2,3' or '(2,3)')\n")

    def find_path(self):
        # Prevent multiple concurrent pathfinding operations
        if self.processing:
            self.output_text.insert(tk.END, "Already processing a path request. Please wait.\n")
            return

        # Check if there are any points to process
        if not self.points:
            self.output_text.insert(tk.END, "Error: No intermediate points added. Please add at least one point.\n")
            return

        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Processing path...\n")
        
        # Set processing flag
        self.processing = True
        
        # Create and start pathfinding thread
        path_thread = threading.Thread(target=self._find_path_thread)
        path_thread.daemon = True  # Thread will be terminated when main program exits
        path_thread.start()
        
        # Start checking for results
        self.root.after(100, self._check_path_results)  # Check for results every 100ms to avoid blocking the GUI

    def _find_path_thread(self):
        try:
            # Define start and end points of the grid
            start_node = (0, 0)
            end_node = (self.grid.rows - 1, self.grid.cols - 1)
            
            # Find path through all points
            path = self.path_finder.find_path_through_points(start_node, self.points, end_node)
            
            if path:
                # Capture visualisation in a string
                old_stdout = sys.stdout
                result = io.StringIO()
                sys.stdout = result
                
                # Generate the path visualisation
                self.path_visualiser.visualise_path(path, start_node, end_node, self.points)
                
                # Restore stdout and get the visualisation
                sys.stdout = old_stdout
                visualisation = result.getvalue()
                
                # Put results in queue
                self.result_queue.put({
                    'success': True,
                    'visualisation': visualisation,
                    'path': path
                })
            else:
                self.result_queue.put({
                    'success': False,
                    'error': "No valid path found through all points"
                })
        except Exception as e:
            self.result_queue.put({
                'success': False,
                'error': str(e)
            })

    def _check_path_results(self):
        try:
            # Check if results are available
            result = self.result_queue.get_nowait()
            
            if result['success']:
                # Display the results in the output area
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, result['visualisation'])
                self.output_text.insert(tk.END, f"\nTotal path length: {len(result['path']) - 1} steps\n")
                
                # Add detailed path sequence
                path_str = " -> ".join([f"({x},{y})" for x, y in result['path']])
                self.output_text.insert(tk.END, f"Path sequence: {path_str}\n")
            else:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, f"Error: {result['error']}\n")
            
            # Reset processing flag
            self.processing = False
            
        except queue.Empty:
            # No results yet, check again in 100ms
            self.root.after(100, self._check_path_results)  # Check again in 100ms to avoid blocking the GUI

    def clear_all(self):
        # Reset all components to initial state
        self.points = []
        self.point_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Cleared all points\n")

def main():
    # Create and start the main application window
    root = tk.Tk()
    app = PathfinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()