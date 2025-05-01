class VisualisationWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Path Visualisation")
        self.window.geometry("800x600")  # Larger window for better grid visibility
        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        # Create canvas for grid visualisation
        self.canvas = tk.Canvas(self.window, bg="white")
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        # Add scrollbars for larger grids
        x_scrollbar = ttk.Scrollbar(self.window, orient="horizontal", command=self.canvas.xview)
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        y_scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        # Add close button
        close_button = ttk.Button(self.window, text="Close", command=self.window.withdraw)
        close_button.grid(row=2, column=0, pady=10)
        # Store grid dimensions and cell size
        self.rows = 0
        self.cols = 0
        self.cell_size = 60  # Default cell size in pixels
        # Initially hide the window
        self.window.withdraw()
    
    def show(self):
        # Center the window
        self.window.deiconify()
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def update_visualisation(self, text):
        # This method was used for basic operations and has been replaced with draw_grid in PathFinderGUI
        pass

class PathfinderGUI:
    def __init__(self, root, rows=10, cols=10):  # Modified to accept dimensions
        # Store the root window and configure basic window properties
        self.root = root
        self.root.title("StockBot")
        self.root.geometry("600x400")
        # Create visualisation window
        self.viz_window = VisualisationWindow(root)
# ...
    def draw_grid(self, rows, cols, path=None, start=None, end=None, points=None):
        # Store grid dimensions
        self.rows = rows
        self.cols = cols
        # Clear previou drawings
        self.canvas.delete("all")
        # Calculate total grid size
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size
        # Configure canvas scrolling region
        self.canvas.configure(scrollregion=(0, 0, grid_width, grid_height))
        
        # Draw grid lines
        for i in range(rows + 1):
            y = i * self.cell_size
            self.canvas.create_line(0, y, grid_width, y, fill="black")
        
        for j in range(cols + 1):
            x = j * self.cell_size
            self.canvas.create_line(x, 0, x, grid_height, fill="black")
        
        # Draw cell IDs
        for i in range(rows):
            for j in range(cols):
                # Calculate position ID (1-based)
                pos_id = (i * cols) + j + 1
                # Calculate cell center
                x = j * self.cell_size + self.cell_size // 2
                y = i * self.cell_size + self.cell_size // 2
                # Draw position ID
                self.canvas.create_text(x, y, text=str(pos_id), font=("Arial", 10))