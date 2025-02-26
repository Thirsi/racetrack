import pygame
import sys
import math
from pygame.locals import *

# This game is not my concept or an original idea, I am just the programmer
# I would name the person who gave me the idea but I don't know his name and
# am too embarrassed to ask.

# Initialize pygame
pygame.init()

# Game window constants
WIDTH, HEIGHT = 800, 600  # Width and height of the game window
FPS = 60  # Frames per second

# Color definitions (RGB values)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)

# Game objects dimensions
BALL_RADIUS = 10
TRACK_INNER_RADIUS = 150  # Inner wall of the circular track
TRACK_OUTER_RADIUS = 250  # Outer wall of the circular track
FRICTION = 0.98  # Friction factor to slow down the ball gradually

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circular Track Game")
clock = pygame.time.Clock()  # For controlling the game's frame rate


class Ball:
    def __init__(self, x, y, radius):
        """Initialize a ball object with position and properties.

        Args:
            x (float): Starting x-coordinate
            y (float): Starting y-coordinate
            radius (int): Radius of the ball in pixels
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 0  # Velocity in x direction
        self.vy = 0  # Velocity in y direction
        self.moving = False  # Is the ball currently in motion?
        self.start_drag_x = 0  # Start position of drag for aiming
        self.start_drag_y = 0  # Start position of drag for aiming
        self.dragging = False  # Is the player currently dragging to aim?

    def update(self, walls):
        """Update the ball's position and handle collisions.

        Args:
            walls (list): A list of wall coordinates to check for collisions
        """
        if self.moving:
            # Calculate the next position based on current velocity
            next_x = self.x + self.vx
            next_y = self.y + self.vy

            # Check collision with walls before moving
            # Calculate distance from track center to check if ball is within track bounds
            next_center_dist = math.sqrt((next_x - WIDTH / 2) ** 2 + (next_y - HEIGHT / 2) ** 2)

            # Check if the ball would be outside the track boundaries after moving
            if next_center_dist - self.radius < TRACK_INNER_RADIUS or next_center_dist + self.radius > TRACK_OUTER_RADIUS:
                # Collision detected, stop the ball immediately
                self.vx = 0
                self.vy = 0
                self.moving = False
            else:
                # No collision, move the ball
                self.x = next_x
                self.y = next_y

                # Apply friction to slow the ball down
                self.vx *= FRICTION
                self.vy *= FRICTION

                # Stop if velocity becomes very small (avoid tiny movements)
                if abs(self.vx) < 0.1 and abs(self.vy) < 0.1:
                    self.vx = 0
                    self.vy = 0
                    self.moving = False

    def draw(self, surface):
        """Draw the ball and aim line if dragging.

        Args:
            surface: Pygame surface to draw on
        """
        # Draw the ball as a red circle
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)

        # Draw aim line when dragging (showing launch direction)
        if self.dragging:
            pygame.draw.line(surface, GREEN, (self.x, self.y),
                             (self.start_drag_x, self.start_drag_y), 2)

    def start_drag(self, x, y):
        """Start dragging from the ball to aim.

        Args:
            x (float): Mouse x-coordinate
            y (float): Mouse y-coordinate
        """
        if not self.moving:  # Only allow aiming if the ball is not moving
            self.dragging = True
            self.start_drag_x = x
            self.start_drag_y = y

    def end_drag(self):
        """End dragging and launch the ball if was being dragged.

        Returns:
            bool: True if the ball was launched, False otherwise
        """
        if self.dragging:
            self.dragging = False
            # Calculate velocity based on drag distance (with a scaling factor)
            # The direction is opposite to the drag (like pulling back a slingshot)
            dx = self.x - self.start_drag_x
            dy = self.y - self.start_drag_y

            # Scale factor to make the launches more powerful
            scale = 0.1

            self.vx = dx * scale
            self.vy = dy * scale
            self.moving = True
            return True  # Indicate that a launch occurred
        return False

    def is_at_finish_line(self, finish_line_points):
        """Check if ball is at the finish line.

        Args:
            finish_line_points (tuple): (x1, y1, x2, y2) coordinates of finish line

        Returns:
            bool: True if the ball is on the finish line, False otherwise
        """
        # This method is now superseded by the check_finish_line function
        # Keeping it for compatibility
        x1, y1, x2, y2 = finish_line_points

        # Calculate distance from ball center to line segment
        line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if line_length == 0:
            return False

        # Projection of ball onto the line
        t = max(0, min(1, ((self.x - x1) * (x2 - x1) + (self.y - y1) * (y2 - y1)) / (line_length ** 2)))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)

        # Distance from ball to closest point on line
        distance = math.sqrt((self.x - proj_x) ** 2 + (self.y - proj_y) ** 2)

        # Check if ball is close to the line and not moving
        return distance < self.radius + 5 and not self.moving


def create_circular_walls():
    """Create the coordinates for inner and outer walls of the circular track.

    Returns:
        tuple: Lists of coordinates for inner and outer walls
    """
    # This function will return the inner and outer wall coordinates
    # Used for visualization, not directly for collision
    inner_wall = []
    outer_wall = []

    center_x, center_y = WIDTH / 2, HEIGHT / 2

    # Create points around the circle at 5-degree intervals
    for angle in range(0, 360, 5):
        rad = math.radians(angle)
        # Calculate inner wall point
        ix = center_x + TRACK_INNER_RADIUS * math.cos(rad)
        iy = center_y + TRACK_INNER_RADIUS * math.sin(rad)
        inner_wall.append((ix, iy))

        # Calculate outer wall point
        ox = center_x + TRACK_OUTER_RADIUS * math.cos(rad)
        oy = center_y + TRACK_OUTER_RADIUS * math.sin(rad)
        outer_wall.append((ox, oy))

    return inner_wall, outer_wall


def check_finish_line(ball, finish_line_points, check_moving=True):
    """Check if ball is crossing or on the finish line.

    Args:
        ball: The ball object
        finish_line_points (tuple): (x1, y1, x2, y2) coordinates of finish line
        check_moving (bool): If True, require ball to be stopped to count as finished

    Returns:
        bool: True if the ball is on/crossing the finish line, False otherwise
    """
    # Extract finish line coordinates
    x1, y1, x2, y2 = finish_line_points

    # Calculate distance from ball center to line segment
    # Using formula for distance from point to line segment
    line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if line_length == 0:
        return False

    # Calculate distance from ball to line
    # Projection of ball onto the line
    t = max(0, min(1, ((ball.x - x1) * (x2 - x1) + (ball.y - y1) * (y2 - y1)) / (line_length ** 2)))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)

    # Distance from ball to closest point on line
    distance = math.sqrt((ball.x - proj_x) ** 2 + (ball.y - proj_y) ** 2)

    # If we're checking for passing the line, we don't care if the ball is moving
    if not check_moving:
        return distance < ball.radius + 5

    # For finish detection, check if ball is close to the line and not moving
    return distance < ball.radius + 5 and not ball.moving


def main():
    """Main game function."""
    # Create walls
    inner_wall, outer_wall = create_circular_walls()

    # Define finish line as a line segment from inner to outer wall at bottom of the track
    center_x, center_y = WIDTH / 2, HEIGHT / 2
    finish_angle = 90  # angle in degrees, 90 means bottom of the circle
    finish_rad = math.radians(finish_angle)

    # Calculate inner and outer points of the finish line
    inner_x = center_x + TRACK_INNER_RADIUS * math.cos(finish_rad)
    inner_y = center_y + TRACK_INNER_RADIUS * math.sin(finish_rad)
    outer_x = center_x + TRACK_OUTER_RADIUS * math.cos(finish_rad)
    outer_y = center_y + TRACK_OUTER_RADIUS * math.sin(finish_rad)

    finish_line_points = (inner_x, inner_y, outer_x, outer_y)

    # Track scores/laps
    best_score = float('inf')  # Start with infinity so any score is better
    laps_completed = 0
    previous_lap_score = 0
    crossed_finish_line = False  # Track if we've already crossed the line (to prevent multiple triggers)

    # Create ball at starting position (to the left of the finish line)
    start_angle = 180  # Place the ball on the left side of the track (180 degrees)
    start_rad = math.radians(start_angle)
    start_radius = TRACK_INNER_RADIUS + (TRACK_OUTER_RADIUS - TRACK_INNER_RADIUS) / 2  # Middle of the track
    ball_x = center_x + start_radius * math.cos(start_rad)
    ball_y = center_y + start_radius * math.sin(start_rad)

    ball = Ball(ball_x, ball_y, BALL_RADIUS)

    # Game state
    move_count = 0
    game_over = False

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and not game_over:
                # Start dragging to aim when clicking
                if not ball.moving:
                    ball.start_drag(event.pos[0], event.pos[1])
            elif event.type == MOUSEMOTION:
                # Update drag position when moving mouse
                if ball.dragging:
                    ball.start_drag_x, ball.start_drag_y = event.pos
            elif event.type == MOUSEBUTTONUP:
                # Release to launch the ball
                if ball.end_drag() and not game_over:
                    move_count += 1  # Increment move counter with each launch
            elif event.type == KEYDOWN:
                if event.key == K_r:  # Reset game when R is pressed
                    ball = Ball(ball_x, ball_y, BALL_RADIUS)
                    move_count = 0
                    game_over = False

        # Update game state
        if not game_over:
            # Update ball position and check for collisions
            ball.update([inner_wall, outer_wall])

            # Check if ball passed through the finish line
            if ball.moving and check_finish_line(ball, finish_line_points, check_moving=False):
                if not crossed_finish_line:
                    # Ball just crossed the finish line
                    crossed_finish_line = True

                    # Lap completed - the key change is here
                    laps_completed += 1
                    previous_lap_score = move_count

                    if move_count < best_score:
                        best_score = move_count

                    # Reset ball position and move counter
                    ball = Ball(ball_x, ball_y, BALL_RADIUS)
                    move_count = 0
            elif not check_finish_line(ball, finish_line_points, check_moving=False):
                crossed_finish_line = False

        # Draw everything
        screen.fill(BLACK)  # Clear screen with black background

        # Draw track - gray circle with black inner circle creates the track
        pygame.draw.circle(screen, GRAY, (WIDTH // 2, HEIGHT // 2), TRACK_OUTER_RADIUS)
        pygame.draw.circle(screen, BLACK, (WIDTH // 2, HEIGHT // 2), TRACK_INNER_RADIUS)

        # Draw finish line - green line across the track
        pygame.draw.line(screen, GREEN, (finish_line_points[0], finish_line_points[1]),
                         (finish_line_points[2], finish_line_points[3]), 5)

        # Draw ball
        ball.draw(screen)

        # Draw move count and stats
        font = pygame.font.Font(None, 36)
        moves_text = font.render(f"Moves: {move_count}", True, WHITE)
        screen.blit(moves_text, (20, 20))

        # Show laps and best score if we've completed any laps
        if laps_completed > 0:
            laps_text = font.render(f"Laps: {laps_completed}", True, WHITE)
            screen.blit(laps_text, (20, 60))

            best_text = font.render(f"Best: {best_score} moves", True, WHITE)
            screen.blit(best_text, (20, 100))

            if previous_lap_score > 0:
                last_lap_text = font.render(f"Previous lap: {previous_lap_score} moves", True, WHITE)
                screen.blit(last_lap_text, (20, 140))

        # Show instructions
        if not ball.moving and not game_over:
            inst_font = pygame.font.Font(None, 24)
            inst_text = inst_font.render("Click and drag from the ball to launch it", True, WHITE)
            screen.blit(inst_text, (WIDTH // 2 - inst_text.get_width() // 2, HEIGHT - 50))

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)  # Maintain consistent frame rate

    # Clean up
    pygame.quit()
    sys.exit()


# Run the game if this script is executed
if __name__ == "__main__":
    main()