# Import logging module for tracking programme execution
import logging
import random  # For genetic algorithm
import math
import time

# Configure logging settings for output formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up logging to write to both file and terminal
file_handler = logging.FileHandler('stockbot_log.txt')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Grid class represents the warehouse structure
class Grid:
    def __init__(self, rows_grid, cols_grid):
        # Store grid dimensions
        self.rows = rows_grid
        self.cols = cols_grid
        # Initialise empty grid with specified dimensions
        self.grid = [[0 for _ in range(cols_grid)] for _ in range(rows_grid)]
        # Track obstacles
        self.obstacles = set()
        
    def add_obstacle(self, row, col):
        """Add an obstacle at the specified position"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.obstacles.add((row, col))
            return True
        return False
        
    def remove_obstacle(self, row, col):
        """Remove an obstacle from the specified position"""
        if (row, col) in self.obstacles:
            self.obstacles.remove((row, col))
            return True
        return False
        
    def is_obstacle(self, row, col):
        """Check if a position contains an obstacle"""
        return (row, col) in self.obstacles

# PathFinder class implements the pathfinding algorithm
class PathFinder:
    def __init__(self, grid_in=None):
        # Store reference to the grid
        self.grid = grid_in
        # Default algorithm
        self.algorithm = "bfs"  # Options: "bfs", "astar"
    
        # Define possible movement directions (up, down, left, right)
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if grid_in:
            logger.info(f"PathFinder initialised with grid size {grid_in.rows}x{grid_in.cols}")

    def bfs(self, start, end):
        # Implements Breadth-First Search algorithm to find shortest path
        logger.info(f"Starting BFS search from {start} to {end}")
        # Validate start and end positions are within grid boundaries
        if not (0 <= start[0] < self.grid.rows and 0 <= start[1] < self.grid.cols):
            logger.error(f"Start position {start} is out of bounds")
            return None
        if not (0 <= end[0] < self.grid.rows and 0 <= end[1] < self.grid.cols):
            logger.error(f"End position {end} is out of bounds")
            return None
        
        # Check if start or end is an obstacle
        if self.grid.is_obstacle(start[0], start[1]) or self.grid.is_obstacle(end[0], end[1]):
            logger.error(f"Start or end position is an obstacle")
            return None
    
        # Initialise queue with starting point and visited set
        queue = [[start]]
        visited = set([start])
        
        # Continue searching while there are paths to explore
        while queue:
            path = queue.pop(0)  # Get the next path to explore
            current = path[-1]   # Get the last position in the path
            
            # If we've reached the end, return the path
            if current == end:
                logger.info(f"Path found with length {len(path)}")
                return path
                
            # Explore all possible directions
            for dx, dy in self.directions:
                nx, ny = current[0] + dx, current[1] + dy
                next_pos = (nx, ny)
                
                # Check if the new position is valid and not visited
                if (0 <= nx < self.grid.rows and 0 <= ny < self.grid.cols and 
                    next_pos not in visited and not self.grid.is_obstacle(nx, ny)):
                    # Create a new path by extending the current path
                    new_path = list(path)
                    new_path.append(next_pos)
                    queue.append(new_path)
                    visited.add(next_pos)
        
        # If we've exhausted all possibilities without finding a path
        logger.warning("No path found")
        return None

    def set_algorithm(self, algorithm):
        """Set the pathfinding algorithm to use"""
        if algorithm in ["bfs", "astar"]:
            self.algorithm = algorithm
            return True
        return False
    
    def find_path(self, start, end):
        """Find path using the selected algorithm"""
        if self.algorithm == "astar":
            return self.astar(start, end)
        else:
            return self.bfs(start, end)
    
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
    
    def find_path_through_points(self, start, points, end, optimise_order=False):
        """
        Finds a path that visits all intermediate points
        
        Parameters:
        - start: Starting position
        - points: List of intermediate points to visit
        - end: End position
        - optimise_order: Whether to optimise the order of points using genetic algorithm
        """
        logger.info(f"Finding path through {len(points)} intermediate points")
        
        if not points:
            logger.warning("No intermediate points provided")
            return self.bfs(start, end)
                
        # If optimise_order is True, find the optimal order to visit points
        if optimise_order and len(points) > 1:
            try:
                # Add timeout for optimisation
                import time
                start_time = time.time()
                
                # Make a copy of points to avoid modifying the original
                points_copy = list(points)
                optimised_points = self.optimise_point_order(start, points_copy, end)
                
                # Check if optimisation took too long
                if time.time() - start_time > 10.0:  # 10 seconds max
                    logger.warning("Optimisation took too long, using original order")
                    # Continue with original points
                else:
                    points = optimised_points
                    logger.info(f"Optimised point order: {points}")
            except Exception as e:
                logger.error(f"Optimisation failed: {str(e)}")
                # Continue with original points
                logger.info("Using original point order")

        # Initialize path construction
        full_path = []
        current_start = start

        # Find path segments between consecutive points
        for i, point in enumerate(points, 1):
            path_segment = self.find_path(current_start, point)  # Use selected algorithm
            if path_segment:
                # Add all points except the last one if not the first segment
                if full_path:
                    full_path.extend(path_segment[1:])
                else:
                    full_path.extend(path_segment)
                current_start = point
            else:
                return None

        # Add final segment from last point to end
        final_segment = self.find_path(current_start, end)  # Use selected algorithm
        if final_segment:
            full_path.extend(final_segment[1:])
        else:
            return None

        return full_path

    def optimise_point_order(self, start, points, end):
        """
        Optimizes the order of points to minimize total path length
        using a genetic algorithm approach
        """
        logger.info("Optimising point order using genetic algorithm")
        
        # If only one point, no optimisation needed
        if len(points) <= 1:
            return points
            
        # Safety check - limit the number of points to optimise
        if len(points) > 10:
            logger.warning(f"Too many points ({len(points)}) for optimisation, limiting to first 10")
            points = points[:10]
            
        # Create initial population (different permutations of points)
        population_size = min(50, math.factorial(len(points)))
        population = []
        
        # Add the original order
        population.append(list(points))
        
        # Add random permutations with a timeout
        start_time = time.time()
        timeout = 2.0  # 2 seconds maximum for population generation
        
        while len(population) < population_size:
            # Check for timeout
            if time.time() - start_time > timeout:
                logger.warning(f"Timeout reached during population generation, using {len(population)} permutations")
                break
                
            perm = list(points)
            random.shuffle(perm)
            if perm not in population:
                population.append(perm)
                
        # Number of generations - reduced for performance
        generations = min(10, 20 if len(points) <= 5 else 10)
        
        # For each generation
        for gen in range(generations):
            # Check for timeout - overall optimisation should not take more than 5 seconds
            if time.time() - start_time > 5.0:
                logger.warning(f"Timeout reached during optimisation at generation {gen}")
                break
                
            # Calculate fitness for each permutation (total path length)
            fitness_scores = []
            
            for perm in population:
                try:
                    # Calculate total path length for this permutation
                    total_length = 0
                    
                    # Path from start to first point
                    path = self.bfs(start, perm[0])
                    if path:
                        total_length += len(path) - 1
                    else:
                        # If no path found, assign a high penalty
                        total_length += 1000
                    
                    # Paths between consecutive points
                    for i in range(len(perm) - 1):
                        path = self.bfs(perm[i], perm[i + 1])
                        if path:
                            total_length += len(path) - 1
                        else:
                            # If no path found, assign a high penalty
                            total_length += 1000
                    
                    # Path from last point to end
                    path = self.bfs(perm[-1], end)
                    if path:
                        total_length += len(path) - 1
                    else:
                        # If no path found, assign a high penalty
                        total_length += 1000
                    
                    fitness_scores.append((total_length, perm))
                except Exception as e:
                    # If any error occurs, assign a high penalty
                    logger.error(f"Error calculating fitness: {str(e)}")
                    fitness_scores.append((10000, perm))
            
            # Sort by fitness (shorter paths are better)
            fitness_scores.sort()
            
            # If we have a good solution, stop early
            if fitness_scores[0][0] < 1000:
                best_perm = fitness_scores[0][1]
                logger.info(f"Found good solution at generation {gen}: {best_perm}")
                return best_perm
            
            # Select top performers (elitism)
            elite_size = max(2, population_size // 5)
            new_population = [score[1] for score in fitness_scores[:elite_size]]
            
            # Fill the rest with crossover and mutation
            while len(new_population) < population_size:
                # Select two parents using tournament selection
                tournament_size = 3
                parent1 = None
                parent2 = None
                
                # Simple timeout check for tournament selection
                selection_start = time.time()
                
                while parent1 is None or parent2 is None:
                    if time.time() - selection_start > 0.5:  # Half second timeout
                        # Just pick random parents if taking too long
                        parent1 = random.choice(population)
                        parent2 = random.choice(population)
                        break
                        
                    # Tournament selection
                    tournament = random.sample(fitness_scores, min(tournament_size, len(fitness_scores)))
                    tournament.sort()
                    
                    if parent1 is None:
                        parent1 = tournament[0][1]
                    else:
                        parent2 = tournament[0][1]
                
                # Perform crossover (ordered crossover)
                try:
                    child = self.ordered_crossover(parent1, parent2)
                    
                    # Perform mutation with low probability
                    if random.random() < 0.1:
                        # Swap mutation - swap two random positions
                        idx1, idx2 = random.sample(range(len(child)), 2)
                        child[idx1], child[idx2] = child[idx2], child[idx1]
                    
                    new_population.append(child)
                except Exception as e:
                    # If crossover fails, just add a copy of the best parent
                    logger.error(f"Crossover error: {str(e)}")
                    new_population.append(parent1.copy())
            
            # Update population for next generation
            population = new_population
        
        # Return the best permutation found
        if fitness_scores:
            return fitness_scores[0][1]
        else:
            # If something went wrong, return original order
            logger.warning("Optimisation failed, returning original order")
            return points
            
    def ordered_crossover(self, parent1, parent2):
        """
        Performs ordered crossover between two parent permutations
        """
        size = len(parent1)
        
        # Choose random subset of parent1
        start, end = sorted(random.sample(range(size), 2))
        
        # Create child with subset from parent1
        child = [None] * size
        for i in range(start, end + 1):
            child[i] = parent1[i]
        
        # Fill remaining positions with values from parent2 in order
        parent2_idx = 0
        for i in range(size):
            if child[i] is None:
                # Find next value from parent2 that's not already in child
                while parent2[parent2_idx] in child:
                    parent2_idx += 1
                    if parent2_idx >= size:
                        # This shouldn't happen with valid permutations, but just in case
                        remaining = [p for p in parent2 if p not in child]
                        if remaining:
                            child[i] = remaining[0]
                            break
                        else:
                            # Emergency fallback - should never reach here
                            child[i] = parent2[0]
                            break
                
                if child[i] is None:  # Still None, means we didn't break from the while loop
                    child[i] = parent2[parent2_idx]
                    parent2_idx += 1
        
        return child
    
    def _mutate(self, permutation):
        """Helper method for genetic algorithm mutation"""
        # Swap two random positions
        idx1, idx2 = random.sample(range(len(permutation)), 2)
        permutation[idx1], permutation[idx2] = permutation[idx2], permutation[idx1]


def validate_point(x, y, rows, cols, allow_start_end=False, obstacles=None):
    """Validates if a point is within bounds and optionally checks for start/end points and obstacles"""
    # Check if point is start/end when not allowed
    if not allow_start_end and ((x, y) == (0, 0) or (x, y) == (rows - 1, cols - 1)):
        return False, f"Cannot use start point (index 1) or end point (index {rows * cols})"
    
    # Check if point is within grid boundaries
    if not (0 <= x < rows and 0 <= y < cols):
        return False, f"Position out of bounds"
    
    # Check if point is an obstacle
    if obstacles and (x, y) in obstacles:
        return False, f"Position contains an obstacle"
    
    return True, ""

# Add after the existing imports
def index_to_coordinates(index, cols):
    """Convert 1-based index to 0-based coordinates"""
    index -= 1  # Convert to 0-based
    row = index // cols
    col = index % cols
    return row, col

def coordinates_to_index(row, col, cols):
    """Convert 0-based coordinates to 1-based index"""
    return (row * cols) + col + 1