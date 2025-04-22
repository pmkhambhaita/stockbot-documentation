import tkinter as tk
from tkinter import ttk, messagebox

class ConfigWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Grid Configuration")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        
        # Initialize result variables
        self.rows = None
        self.cols = None
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create and configure grid inputs
        ttk.Label(main_frame, text="Grid Dimensions").grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Rows input
        ttk.Label(main_frame, text="Rows:").grid(row=1, column=0, padx=5, pady=5)
        self.rows_spinbox = ttk.Spinbox(main_frame, from_=1, to=50, width=10)
        self.rows_spinbox.grid(row=1, column=1, padx=5, pady=5)
        self.rows_spinbox.set(10)  # Default value
        
        # Columns input
        ttk.Label(main_frame, text="Columns:").grid(row=2, column=0, padx=5, pady=5)
        self.cols_spinbox = ttk.Spinbox(main_frame, from_=1, to=50, width=10)
        self.cols_spinbox.grid(row=2, column=1, padx=5, pady=5)
        self.cols_spinbox.set(10)  # Default value
        
        # Confirm button
        ttk.Button(main_frame, text="Confirm", command=self.validate_and_save).grid(
            row=3, column=0, columnspan=2, pady=20)
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def validate_and_save(self):
        try:
            rows = int(self.rows_spinbox.get())
            cols = int(self.cols_spinbox.get())
            
            if rows <= 0 or cols <= 0:
                messagebox.showerror("Invalid Input", "Rows and columns must be positive numbers.")
                return
            
            if rows > 50 or cols > 50:
                messagebox.showerror("Invalid Input", "Maximum grid size is 50x50.")
                return
            
            self.rows = rows
            self.cols = cols
            self.root.destroy()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers.")
    
    def get_dimensions(self):
        self.root.mainloop()
        return self.rows, self.cols

def get_grid_config():
    config_window = ConfigWindow()
    return config_window.get_dimensions()