import tkinter as tk
from tkinter import ttk, messagebox

class ConfigWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("StockBot Setup")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Initialize result variables
        self.rows = None
        self.cols = None
        self.current_page = 0
        
        # Configure root grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        
        # Create content frame (will hold different pages)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=1, column=0, sticky="se", pady=(20, 0))
        
        # Create navigation buttons
        self.back_button = ttk.Button(self.button_frame, text="Back", command=self.go_back, state=tk.DISABLED)
        self.next_button = ttk.Button(self.button_frame, text="Next", command=self.go_next)
        self.finish_button = ttk.Button(self.button_frame, text="Finish", command=self.finish, state=tk.DISABLED)
        
        # Grid buttons (right-aligned)
        self.back_button.grid(row=0, column=0, padx=5)
        self.next_button.grid(row=0, column=1, padx=5)
        self.finish_button.grid(row=0, column=2, padx=5)
        
        # Create pages list with all pages
        self.pages = [
            self.create_welcome_page,
            self.create_config_page,
            self.create_guide_page
        ]
        
        # Show first page
        self.show_page(0)
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_welcome_page(self, frame):
        # Configure frame grid
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        
        # Logo or icon (placeholder)
        logo_label = ttk.Label(frame, text="StockBot", font=("Arial", 24, "bold"))
        logo_label.grid(row=0, column=0, pady=20)
        
        # Welcome message
        welcome_label = ttk.Label(
            frame, 
            text="Welcome to StockBot, the simple warehouse management system!\nPress Next to begin configuration.",
            font=("Arial", 12),
            justify=tk.CENTER
        )
        welcome_label.grid(row=1, column=0, pady=20)
    
    def create_config_page(self, frame):
        # Configure frame grid
        frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(frame, text="Grid Configuration", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Configuration inputs
        config_frame = ttk.Frame(frame)
        config_frame.grid(row=1, column=0, pady=20)
        
        # Rows input
        ttk.Label(config_frame, text="Rows:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.rows_spinbox = ttk.Spinbox(config_frame, from_=1, to=50, width=10, font=("Arial", 12))
        self.rows_spinbox.grid(row=0, column=1, padx=10, pady=10)
        self.rows_spinbox.set(10)  # Default value
        
        # Columns input
        ttk.Label(config_frame, text="Columns:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.cols_spinbox = ttk.Spinbox(config_frame, from_=1, to=50, width=10, font=("Arial", 12))
        self.cols_spinbox.grid(row=1, column=1, padx=10, pady=10)
        self.cols_spinbox.set(10)  # Default value
        
        # Description
        desc_label = ttk.Label(
            frame, 
            text="Configure the size of your warehouse grid.\nLarger grids can represent bigger warehouses but may be slower.",
            font=("Arial", 10),
            justify=tk.CENTER
        )
        desc_label.grid(row=2, column=0, pady=20)
    
    def create_guide_page(self, frame):
        # Configure frame grid
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(frame, text="Basic Operations Guide", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Guide content
        guide_frame = ttk.Frame(frame)
        guide_frame.grid(row=1, column=0, sticky="nsew")
        guide_frame.grid_columnconfigure(0, weight=1)
        guide_frame.grid_rowconfigure(0, weight=1)
        
        guide_text = tk.Text(guide_frame, wrap=tk.WORD, height=12, font=("Arial", 10))
        guide_text.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(guide_frame, orient="vertical", command=guide_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        guide_text.configure(yscrollcommand=scrollbar.set)
        
        # Insert guide content
        guide_content = """
StockBot Basic Operations:

1. Add Point: Enter a position number and click "Add Point" to add it to your path.

2. Find Path: Click "Find Path" to calculate the optimal route through all added points.

3. Clear: Reset all points and start over.

4. Query Stock: Check the current stock level at a specific position.

5. Update Stock: Modify the stock quantity at a specific position.
        """
        guide_text.insert(tk.END, guide_content)
        guide_text.config(state=tk.DISABLED)  # Make read-only
    
    def show_page(self, page_index):
        # Clear current page
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create new page
        self.pages[page_index](self.content_frame)
        self.current_page = page_index
        
        # Update button states
        self.back_button.config(state=tk.NORMAL if page_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if page_index < len(self.pages) - 1 else tk.DISABLED)
        self.finish_button.config(state=tk.NORMAL if page_index == len(self.pages) - 1 else tk.DISABLED)
    
    def go_back(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)
    
    def go_next(self):
        if self.current_page < len(self.pages) - 1:
            # If leaving config page, validate inputs
            if self.current_page == 1:
                if not self.validate_config():
                    return
            self.show_page(self.current_page + 1)
    
    def validate_config(self):
        try:
            rows = int(self.rows_spinbox.get())
            cols = int(self.cols_spinbox.get())
            
            if rows <= 0 or cols <= 0:
                messagebox.showerror("Invalid Input", "Rows and columns must be positive numbers.")
                return False
            
            if rows > 50 or cols > 50:
                messagebox.showerror("Invalid Input", "Maximum grid size is 50x50.")
                return False
            
            self.rows = rows
            self.cols = cols
            return True
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers.")
            return False
    
    def finish(self):
        if self.rows is None or self.cols is None:
            if not self.validate_config():
                return
        self.root.destroy()
    
    def get_dimensions(self):
        self.root.mainloop()
        return self.rows, self.cols

def get_grid_config():
    config_wizard = ConfigWizard()
    return config_wizard.get_dimensions()