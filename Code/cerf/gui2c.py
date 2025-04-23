# Import required libraries for GUI, file operations and system functions
import tkinter as tk
from tkinter import ttk  # Themed widgets for enhanced GUI appearance
import spa1c as spa              # Custom module for pathfinding algorithms
import io              # For redirecting stdout to capture visualisation
import sys             # For system-level operations like stdout manipulation
import threading       # For multi-threading support
import queue           # For thread-safe data exchange
import config1c as config
import database2c as database

class PathfinderGUI:
'''
........
'''

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
