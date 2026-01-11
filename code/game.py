# Standard library imports
import time
import sys
import random

# Attempt to import curses module with error handling
try:
    import curses
except:
    print("Error: problem importing the 'curses' module.\n\nThis program requires the 'curses' module to run. Please ensure that your Python installation includes it. If on Windows, you may need to install the 'windows-curses' package via pip:\npip install windows-curses")
    sys.exit(1)

# Multiline string constants
TITLE = """
 █████╗ ███████╗████████╗███████╗██████╗  ██████╗ ██╗██████╗ 
██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██╔═══██╗██║██╔══██╗
███████║███████╗   ██║   █████╗  ██████╔╝██║   ██║██║██║  ██║
██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║   ██║██║██║  ██║
██║  ██║███████║   ██║   ███████╗██║  ██║╚██████╔╝██║██████╔╝
╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝╚═════╝ 
                                                             
███████╗██╗  ██╗ ██████╗  ██████╗ ████████╗███████╗██████╗   
██╔════╝██║  ██║██╔═══██╗██╔═══██╗╚══██╔══╝██╔════╝██╔══██╗  
███████╗███████║██║   ██║██║   ██║   ██║   █████╗  ██████╔╝  
╚════██║██╔══██║██║   ██║██║   ██║   ██║   ██╔══╝  ██╔══██╗  
███████║██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████╗██║  ██║  
╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝  
""".splitlines()

GAMEOVER = """
 ██████╗  █████╗ ███╗   ███╗███████╗
██╔════╝ ██╔══██╗████╗ ████║██╔════╝
██║  ███╗███████║██╔████╔██║█████╗  
██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  
╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗
 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
                                    
 ██████╗ ██╗   ██╗███████╗██████╗   
██╔═══██╗██║   ██║██╔════╝██╔══██╗  
██║   ██║██║   ██║█████╗  ██████╔╝  
██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗  
╚██████╔╝ ╚████╔╝ ███████╗██║  ██║  
 ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝  
""".splitlines()

# Global variables
explosions = []
players = []
bullets = []
asteroids = []
asteroid_symbols = ("@", "%", "&", "0", "Q", "X")
explode_anim = (("     ", "     ", "  #  ", "     ", "     "), 
                ("     ", "  #  ", " ### ", "  #  ", "     "),
                ("     ", "  #  ", "#####", "  #  ", "     "),
                ("  #  ", "#####", "#   #", "#####", "  #  "),
                (" ### ", "#   #", "#   #", "#   #", " ### "),
                ("     ", "     ", "     ", "     ", "     "))


# -------------- Helper Functions ----------------

# Function to round values to nearest integer for grid placement
def grid(value):
    return int(round(value, 0))

# Function to check collision between two objects
def check_collision(obj1, obj2):
    return (abs(obj1.pos.x - obj2.pos.x) < 1) and (abs(obj1.pos.y - obj2.pos.y) < 1)

# Function for static UI
def draw_ui(stdscr, LINES):
    for player in players:
        stdscr.addstr(LINES // 2 - 15 + (players.index(player) * 4), 2, f"{player.name}", curses.A_BOLD | curses.A_UNDERLINE)
        stdscr.addstr(LINES // 2 - 15 + (1 + players.index(player) * 4), 2, f"Lives: {player.lives}")
        stdscr.addstr(LINES // 2 - 15 + (2 + players.index(player) * 4), 2, f"Points: {player.pts}")

# -------------- Game Classes ----------------

# Explosion class for handling explosion animations
class Explosion:
    def __init__(self, centerX, centerY):
        self.centerX = centerX
        self.centerY = centerY
        self.cur_frame = 0
        self.last_update = time.monotonic()

    def draw(self, gameWin):
        if self.cur_frame >= len(explode_anim) or self.centerY - 2 < 0 or self.centerY + 2 >= 30 or self.centerX - 2 < 0 or self.centerX + 2 >= 70:
            explosions.remove(self)
            return
        if time.monotonic() - self.last_update < 0.1:
            return
        for line in range(5):
            gameWin.addstr(self.centerY - 2 + line, self.centerX - 2, explode_anim[self.cur_frame][line])
        self.last_update = time.monotonic()
        self.cur_frame += 1

# Coordinate class for position handling
class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Bullet class for handling player shots
class Bullet:
    def __init__(self, playerShot):
        self.pos = Coordinate(playerShot.pos.x, playerShot.pos.y - 1)
        self.symbol = "|"
        self.playerShot = playerShot

    def move(self, gameWin):
        gameWin.addstr(grid(self.pos.y), grid(self.pos.x), ' ')  # Clear previous position
        self.pos.y -= 1  # Move bullet up
        if self.pos.y > 0:
            gameWin.addstr(grid(self.pos.y), grid(self.pos.x), self.symbol)  # Draw bullet
        else:
            return False  # Bullet is out of bounds
        return True  # Bullet is still in bounds

# Asteroid class for handling falling asteroids
class Asteroid:
    def __init__(self):
        self.symbol = random.choice(asteroid_symbols)
        self.pos = Coordinate(random.randint(1, 68), 1)
        self.speed = round(random.uniform(0.1, 0.7), 2)

    def move(self, gameWin, player, stdscr, LINES):
        gameWin.addstr(grid(self.pos.y), grid(self.pos.x), ' ')  # Clear previous position
        self.pos.y += self.speed  # Move asteroid down
        if self.pos.y < 28:
            if check_collision(self, player):
                player.lives -= 1  # Decrease player lives on collision
                draw_ui(stdscr, LINES)
                if not (self.pos.x - 3 <= 0 or self.pos.x + 3 >= 70 or self.pos.y - 3 <= 0 or self.pos.y + 3 >= 30):
                    explosions.append(Explosion(grid(self.pos.x), grid(self.pos.y)))
                stdscr.refresh()
                return False  # Asteroid is removed on collision
            gameWin.addstr(grid(self.pos.y), grid(self.pos.x), self.symbol)  # Draw asteroid

        else:
            return False  # Asteroid is out of bounds
        return True  # Asteroid is still in bounds

# Player class for handling player properties and movements
class Player:
    def __init__(self, name, pts, x, leftKey, rightKey, shootKey):
        self.name = name
        self.pts = pts
        self.lives = 3
        self.pos = Coordinate(x, 25)
        self.symbol = "A"
        self.leftKey = leftKey
        self.rightKey = rightKey
        self.shootKey = shootKey
        self.dir = 1


    def move_left(self, gameWin):
        gameWin.addstr(self.pos.y, self.pos.x, ' ')  # Clear previous position
        self.pos.x = max(1, self.pos.x - 1) # Update x position with boundary check
        gameWin.addstr(self.pos.y, self.pos.x, self.symbol)  # Draw player
    
    def move_right(self, gameWin):
        gameWin.addstr(self.pos.y, self.pos.x, ' ')  # Clear previous position
        self.pos.x = min(67, self.pos.x + 1) # Update x position with boundary check
        gameWin.addstr(self.pos.y, self.pos.x, self.symbol)  # Draw player


# -------------- Game Function ----------------

def main(stdscr):
    # Cursor hide
    try:
        curses.curs_set(0)
        cursor_hidden = True
    except:
        cursor_hidden = False
    
    # Variables for game
    last_update = time.monotonic()
    FPS = 30
    LINES, COLS = stdscr.getmaxyx()

    # Ensure terminal size is sufficient
    if COLS < 120 or LINES < 30:
        stdscr.addstr(0, 0, "Error: Terminal window too small. Click any key to end.")
        stdscr.refresh()
        stdscr.getch()
        return

    # Display title screen
    stdscr.clear()
    for i in range(len(TITLE)):
        stdscr.addstr(int(LINES // 2) + i - (len(TITLE) // 2), int((COLS - len(TITLE[i])) // 2), TITLE[i])
    stdscr.addstr(LINES - 2, 2, "Press any key to start... q to quit.")
    stdscr.addstr(LINES - 5, 4, "*The game may not show correctly if not in full screen.", curses.A_BOLD | curses.A_ITALIC)
    stdscr.refresh()
    key = stdscr.getch()
    if key == ord('q'):
        return 

    # Setup before main loop
    stdscr.clear()
    stdscr.addstr(LINES // 2, COLS // 2 - 40, "Press '1' for Single Player Mode. Press '2' for Two Player Mode.")
    stdscr.addstr(LINES // 2 + 3, COLS // 2 - 40, "Player 1 Controls: A - Left, D - Right, W - Shoot")
    stdscr.addstr(LINES // 2 + 4, COLS // 2 - 40, "Player 2 Controls: J - Left, L - Right, I - Shoot")
    stdscr.refresh()
    while True:
        mode_key = stdscr.getch()
        if mode_key == ord('2'):
            multiplayer = True
            break
        elif mode_key == ord('1'):
            multiplayer = False
            break

    stdscr.clear()
    if multiplayer:
        players.append(Player("Player 1", 0, 20, ord('a'), ord('d'), ord('w')))
        players.append(Player("Player 2", 0, 40, ord('j'), ord('l'), ord('i')))
    else:
        players.append(Player("Player 1", 0, COLS // 2, ord('a'), ord('d'), ord('w')))

    gameWin = curses.newwin(30, 70, (LINES - 30) // 2, (COLS - 70) // 2)
    gameWin.border()
    gameWin.nodelay(True)
    gameWin.keypad(True)
    stdscr.refresh()
    gameWin.refresh()

    # Static UI
    for i in range(len(players)):
        draw_ui(stdscr, LINES)
    stdscr.refresh()

    # Main game loop
    while True:
        # Get user input and update time
        last_update = time.monotonic()
        cur_key = gameWin.getch()
        if cur_key == ord('q'):
            break
        for player in players:
            match cur_key:
                case player.leftKey:
                    player.dir = -1
                    break
                case player.rightKey:
                    player.dir = 1
                    break
                case player.shootKey:
                    bullets.append(Bullet(player))
                    break

        # Check death
        for player in players:
            if player.lives == 0:
                # Remove game window
                gameWin.clear()
                gameWin.refresh()
                del gameWin
                # Display game over screen
                stdscr.clear()
                for i in range(len(GAMEOVER)):
                    stdscr.addstr(int(LINES // 2) + i - (len(GAMEOVER) // 2), int((COLS - len(GAMEOVER[i])) // 2), GAMEOVER[i])
                stdscr.addstr(LINES // 2 + (len(GAMEOVER) // 2) + 2, int((COLS - 22) // 2), f"Final Score:", curses.A_BOLD)
                for player in players:
                    stdscr.addstr(LINES // 2 + (len(GAMEOVER) // 2) + players.index(player) + 4, int((COLS - 20) // 2), f"{player.name}: {player.pts} points")
                stdscr.addstr(LINES - 2, 2, "Press the ENTER key to end.", curses.A_ITALIC)
                stdscr.refresh()
                stdscr.nodelay(False)
                while True:
                    end_key = stdscr.getch()
                    if end_key == ord('\n') or end_key == ord('\r'):
                        break
                return

        # Update player position based on input
        for player in players:
            if player.dir == -1:
                player.move_left(gameWin)
            elif player.dir == 1:
                player.move_right(gameWin)
        
        # Bullet stuff
        for bullet in bullets[:]:
            if not bullet.move(gameWin):
                bullets.remove(bullet)

        # Asteroid stuff
        if random.randint(1, 50) == 1:
            asteroids.append(Asteroid())
        
        for asteroid in asteroids[:]:
            if not asteroid.move(gameWin, players[0], stdscr, LINES):
                asteroids.remove(asteroid)
        
        # Bullet-Asteroid collision check
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                if check_collision(bullet, asteroid):
                    gameWin.addstr(grid(bullet.pos.y), grid(bullet.pos.x), ' ')  # Clear bullet
                    gameWin.addstr(grid(asteroid.pos.y), grid(asteroid.pos.x), ' ')  # Clear asteroid
                    bullets.remove(bullet)
                    asteroids.remove(asteroid)
                    explosions.append(Explosion(grid(asteroid.pos.x), grid(asteroid.pos.y)))
                    bullet.playerShot.pts += 1
                    draw_ui(stdscr, LINES)
                    stdscr.refresh()
                    break  # Exit inner loop to avoid further checks with this bullet
        
        # Update explosions
        for explosion in explosions[:]:
            explosion.draw(gameWin)
        
        # Refresh window
        if not cursor_hidden:
            gameWin.addstr(28, 68, " ") 
        gameWin.refresh()
        time.sleep(max(0, (1 / FPS) - (time.monotonic() - last_update)))

# Initialize game
curses.wrapper(main)