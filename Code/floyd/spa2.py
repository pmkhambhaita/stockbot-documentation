class PathFinder:
    # ...
    
    def set_algorithm(self, algorithm):
        """Set the pathfinding algorithm"""
        self.algorithm = algorithm 
    def astar(self, start, end):
        """
        A* pathfinding algorithm implementation
        
        Parameters:
        - start: Starting position (row, col)
        - end: End position (row, col)
        
        Returns:
        - List of positions forming the path from start to end, or None if no path found
        """
        if not self.grid:
            return None
            
        # Check if start and end are valid using the existing validate_point function
        valid_start, _ = validate_point(start[0], start[1], self.grid.rows, self.grid.cols, allow_start_end=True)
        valid_end, _ = validate_point(end[0], end[1], self.grid.rows, self.grid.cols, allow_start_end=True)
        
        if not valid_start or not valid_end:
            return None
            
        # Check if start and end are the same
        if start == end:
            return [start]
            
        # Priority queue for A* (f_score, position)
        import heapq
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        # Dictionaries to store g_score and f_score
        g_score = {start: 0}  # Cost from start to current node
        f_score = {start: self.heuristic(start, end)}  # Estimated total cost
        
        # Dictionary to reconstruct path
        came_from = {}
        
        # Set of visited nodes
        closed_set = set()
        
        while open_set:
            # Get node with lowest f_score
            current_f, current = heapq.heappop(open_set)
            
            # If we reached the end, reconstruct and return the path
            if current == end:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
                
            # Add current to closed set
            closed_set.add(current)
            
            # Check all neighbors (up, down, left, right)
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                neighbor_row, neighbor_col = current[0] + dr, current[1] + dc
                
                # Use validate_point to check if neighbor is valid
                valid, _ = validate_point(neighbor_row, neighbor_col, self.grid.rows, self.grid.cols, allow_start_end=True)
                if not valid:
                    continue
                    
                neighbor = (neighbor_row, neighbor_col)
                
                # Skip if in closed set
                if neighbor in closed_set:
                    continue
                    
                # Calculate tentative g_score
                tentative_g = g_score[current] + 1  # Assuming uniform cost of 1
                
                # If neighbor not in open set or has better g_score
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    # Update path and scores
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, end)
                    
                    # Add to open set if not already there
                    if neighbor not in [item[1] for item in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # No path found
        return None
    
    def heuristic(self, a, b):
        """
        Manhattan distance heuristic for A*
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])



class PathfinderGUI:
    def __init__(self, root, rows=10, cols=10):  # Modified to accept dimensions
        # Store the root window and configure basic window properties
        self.root = root
        self.root.title("StockBot")

        # ...

    def create_menu_bar(self):
        """Create the menu bar with options"""
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # Create File menu
        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Create Algorithm menu
        algorithm_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Algorithm", menu=algorithm_menu)
        
        # Add algorithm selection
        self.algorithm_var = tk.StringVar(value=self.algorithm)
        algorithm_menu.add_radiobutton(
            label="Breadth-First Search (BFS)", 
            variable=self.algorithm_var,
            value="bfs",
            command=self.set_algorithm
        )
        algorithm_menu.add_radiobutton(
            label="A* Search", 
            variable=self.algorithm_var,
            value="astar",
            command=self.set_algorithm
        )
        
        # Create Options menu
        options_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Options", menu=options_menu)
        
        # Add optimisation toggle
        self.optimise_var = tk.BooleanVar(value=self.optimise_order)
        options_menu.add_checkbutton(
            label="Optimise Point Order", 
            variable=self.optimise_var,
            command=self.toggle_optimisation
        )
        
        # Create Help menu
        help_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def set_algorithm(self):
        """Set the pathfinding algorithm"""
        algorithm = self.algorithm_var.get()
        self.algorithm = algorithm
        self.path_finder.set_algorithm(algorithm)
        
        # Display message about algorithm change
        algorithm_name = "Breadth-First Search" if algorithm == "bfs" else "A* Search"
        self.output_text.insert(tk.END, f"Pathfinding algorithm set to: {algorithm_name}\n")
        
    def toggle_optimisation(self):
        """Toggle the optimisation setting"""
        self.optimise_order = self.optimise_var.get()
        status = "enabled" if self.optimise_order else "disabled"
        self.output_text.insert(tk.END, f"Point order optimisation {status}\n")

    def show_about(self):
        """Show about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About StockBot")
        about_window.geometry("300x200")
        
        ttk.Label(
            about_window, 
            text="StockBot Pathfinding System",
            font=("Arial", 12, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            about_window, 
            text="A warehouse navigation system\nwith stock management capabilities.",
            justify="center"
        ).pack(pady=5)
        
        ttk.Label(
            about_window, 
            text="© 2025 StockBot Team",
            font=("Arial", 8)
        ).pack(pady=20)
        
        ttk.Button(
            about_window, 
            text="Close", 
            command=about_window.destroy
        ).pack(pady=10)