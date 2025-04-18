# Import logging module for tracking programme execution
import logging

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

# PathFinder class implements the pathfinding algorithm
class PathFinder:
    def __init__(self, grid_in=None):
        # Store reference to the grid
        self.grid = grid_in
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

        # Initialise queue with starting point and visited set
        queue = [[start]]
        visited = set()
        
        # Continue searching while there are paths to explore
        while queue:
            path = queue.pop(0)  # Get the next path to explore
            x, y = path[-1]      # Get the last point in the path

            # Check if we've reached the destination
            if (x, y) == end:
                logger.info(f"Path found with length {len(path) - 1}")
                return path

            # Explore unvisited neighbours
            if (x, y) not in visited:
                visited.add((x, y))
                for dx, dy in self.directions:
                    nx, ny = x + dx, y + dy  # Calculate neighbour coordinates
                    # Check if neighbour is within bounds
                    if 0 <= nx < self.grid.rows and 0 <= ny < self.grid.cols:
                        if (nx, ny) not in visited:
                            new_path = list(path) + [(nx, ny)]
                            queue.append(new_path)

        logger.warning(f"No path found between {start} and {end}")
        return None

    def find_path_through_points(self, start, points, end):
        # Finds a path that visits all intermediate points in order
        logger.info(f"Finding path through {len(points)} intermediate points")
        if not points:
            logger.warning("No intermediate points provided")
            return self.bfs(start, end)

        # Initialise path construction
        full_path = []
        current_start = start

        # Find path segments between consecutive points
        for i, point in enumerate(points, 1):
            logger.debug(f"Finding path segment {i} to point {point}")
            path_segment = self.bfs(current_start, point)
            if path_segment:
                full_path.extend(path_segment[:-1])
                current_start = point
            else:
                logger.error(f"Failed to find path segment to point {point}")
                return None

        # Find final path segment to end point
        final_segment = self.bfs(current_start, end)
        if final_segment:
            full_path.extend(final_segment)
            logger.info(f"Complete path found with length {len(full_path) - 1}")
            return full_path
        else:
            logger.error(f"Failed to find final path segment to end point {end}")
            return None

# PathVisualiser class handles the visual representation of the path
class PathVisualiser:
    def __init__(self, grid_in):
        # Store reference to the grid
        self.grid = grid_in
        logger.info(f"PathVisualiser initialised with grid size {grid_in.rows}x{grid_in.cols}")

    def visualise_path(self, path, start, end, points=None):
        # Creates a visual representation of the path using ASCII characters
        # [ ] represents empty cells
        # [=] represents path segments
        # [*] represents start, end, and intermediate points
        if points is None:
            points = []
        if not path:
            logger.error("Cannot visualise: path is empty or None")
            return

        logger.info("Starting path visualisation")
        try:
            # Create empty visual grid
            visual_grid = [['[ ]' for _ in range(self.grid.cols)] for _ in range(self.grid.rows)]

            # Mark path segments
            for (x, y) in path:
                visual_grid[x][y] = '[=]'

            # Mark start and end points
            sx, sy = start
            ex, ey = end
            visual_grid[sx][sy] = '[*]'
            visual_grid[ex][ey] = '[*]'
            
            # Mark intermediate points
            for x, y in points:
                valid, _ = validate_point(x, y, self.grid.rows, self.grid.cols, True)
                if valid:
                    visual_grid[x][y] = '[*]'
                else:
                    logger.warning(f"Point ({x}, {y}) is out of bounds and will be skipped")

            # Display the grid
            for row in visual_grid:
                print(' '.join(row))
            
            logger.info("Path visualisation completed")
        except Exception as _e_:
            logger.error(f"Error during visualisation: {str(_e_)}")

def validate_point(x, y, rows, cols, allow_start_end=False):
    """Validates if a point is within bounds and optionally checks for start/end points
    Returns: (bool, str) - (is_valid, error_message)"""
    # Check if point is start/end when not allowed
    if not allow_start_end and ((x, y) == (0, 0) or (x, y) == (rows - 1, cols - 1)):
        return False, f"Cannot use start point (0,0) or end point ({rows-1},{cols-1})"
    
    # Check if point is within grid boundaries
    if not (0 <= x < rows and 0 <= y < cols):
        return False, f"Coordinates ({x},{y}) out of bounds"
    
    return True, ""