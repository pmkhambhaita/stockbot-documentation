import logging

# Configure logging with timestamp and level
# Important for debugging and tracking program flow
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Grid:
    """
    Represents the warehouse grid structure.
    Simple 2D grid implementation using nested lists.
    """
    def __init__(self, rows_grid, cols_grid):
        self.rows = rows_grid
        self.cols = cols_grid
        # Initialise empty grid - 0 represents empty cells
        self.grid = [[0 for _ in range(cols_grid)] for _ in range(rows_grid)]

class PathFinder:
    """
    Implements pathfinding algorithm using Breadth-First Search.
    BFS guarantees shortest path in unweighted grid.
    """
    def __init__(self, grid_in):
        self.grid = grid_in
        # Four directions of movement (up, down, left, right)
        # Diagonal movement not allowed for simplicity
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        logger.info(f"PathFinder initialised with grid size {grid_in.rows}x{grid_in.cols}")

    def bfs(self, start, end):
        """
        Breadth-First Search implementation.
        Returns shortest path between start and end points.
        Validation needed to ensure points are within grid.
        """
        logger.info(f"Starting BFS search from {start} to {end}")
        # Validate start and end positions
        if not (0 <= start[0] < self.grid.rows and 0 <= start[1] < self.grid.cols):
            logger.error(f"Start position {start} is out of bounds")
            return None
        if not (0 <= end[0] < self.grid.rows and 0 <= end[1] < self.grid.cols):
            logger.error(f"End position {end} is out of bounds")
            return None

        queue = [[start]]
        visited = set()
        
        while queue:
            path = queue.pop(0)
            x, y = path[-1]

            if (x, y) == end:
                logger.info(f"Path found with length {len(path) - 1}")
                return path

            if (x, y) not in visited:
                visited.add((x, y))
                # Check all four directions
                for dx, dy in self.directions:
                    nx, ny = x + dx, y + dy
                    # Validate new position is within grid
                    if 0 <= nx < self.grid.rows and 0 <= ny < self.grid.cols:
                        if (nx, ny) not in visited:
                            new_path = list(path) + [(nx, ny)]
                            queue.append(new_path)

        logger.warning(f"No path found between {start} and {end}")
        return None

    def find_path_through_points(self, start, points, end):
        """
        Finds complete path through all intermediate points.
        Connects multiple path segments to create full route.
        """
        logger.info(f"Finding path through {len(points)} intermediate points")
        if not points:
            logger.warning("No intermediate points provided")
            return self.bfs(start, end)

        full_path = []
        current_start = start

        # Find path segments between consecutive points
        for i, point in enumerate(points, 1):
            logger.debug(f"Finding path segment {i} to point {point}")
            path_segment = self.bfs(current_start, point)
            if path_segment:
                # Avoid duplicate points between segments
                full_path.extend(path_segment[:-1])
                current_start = point
            else:
                logger.error(f"Failed to find path segment to point {point}")
                return None

        # Connect final point to end position
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
            visual_grid = [['[ ]' for _ in range(self.grid.cols)] for _ in range(self.grid.rows)]

            for (x, y) in path:
                visual_grid[x][y] = '[=]'

            sx, sy = start
            ex, ey = end
            visual_grid[sx][sy] = '[*]'
            visual_grid[ex][ey] = '[*]'
            
            for x, y in points:
                if 0 <= x < self.grid.rows and 0 <= y < self.grid.cols:
                    visual_grid[x][y] = '[*]'
                else:
                    logger.warning(f"Point ({x}, {y}) is out of bounds and will be skipped")

            for row in visual_grid:
                print(' '.join(row))
            
            logger.info("Path visualisation completed")
        except Exception as _e_:
            logger.error(f"Error during visualisation: {str(_e_)}")

def get_valid_coordinate(prompt, max_rows, max_cols):
    # Helper function to get and validate coordinate input from user
    # Ensures coordinates are within grid boundaries and properly formatted
    while True:
        try:
            coord_input = input(prompt)
            # Remove parentheses and whitespace from input
            coord_input = coord_input.strip('()').replace(' ', '')
            x, y = map(int, coord_input.split(','))
            
            # Validate coordinates are within grid boundaries
            if 0 <= x < max_rows and 0 <= y < max_cols:
                return x, y
            else:
                logger.warning(f"Coordinates ({x},{y}) out of bounds. Must be within (0-{max_rows-1}, 0-{max_cols-1})")
        except ValueError:
            logger.error("Invalid input format. Please use 'x,y' format with numbers")

def get_points(rows_in, cols_in):
    # Handles the collection of intermediate points from user input
    try:
        while True:
            num_points = input("Enter the number of intermediate points (0 or more): ")
            try:
                num_points = int(num_points)
                if num_points >= 0:
                    break
                logger.warning("Number of points must be non-negative")
            except ValueError:
                logger.error("Please enter a valid number")

        # Collect all intermediate points
        points = []
        for i in range(num_points):
            logger.info(f"Entering point {i+1} of {num_points}")
            point = get_valid_coordinate(
                f"Enter point {i+1} coordinates (x,y): ",
                rows_in,
                cols_in
            )
            points.append(point)
            logger.info(f"Added point {point}")

        return points

    except KeyboardInterrupt:
        logger.warning("\nInput cancelled by user")
        return None
