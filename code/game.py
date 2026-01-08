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

asteroidsSymbols = ["@", "#", "%", "&", "0", "Q", "X"]

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Bullet:
    def __init__(self, playerShot):
        self.pos = Coordinate(playerShot.pos.x, playerShot.pos.y - 1)
        self.symbol = "|"

    def move(self, gameWin, asteroids):
        gameWin.addstr(int(round(self.pos.y, 0)), int(round(self.pos.x, 0)), ' ')  # Clear previous position
        self.pos.y -= 1  # Move bullet up
        if self.pos.y > 0:
            gameWin.addstr(int(round(self.pos.y, 0)), int(round(self.pos.x, 0)), self.symbol)  # Draw bullet
        else:
            return False  # Bullet is out of bounds
        return True  # Bullet is still in bounds
class Asteroid:
    def __init__(self):
        self.symbol = random.choice(asteroidsSymbols)
        self.pos = Coordinate(random.randint(1, 68), 1)
        self.speed = round(random.uniform(0.1, 0.7), 2)
    def move(self, gameWin, p1, stdscr, LINES):
        gameWin.addstr(int(round(self.pos.y, 0)), int(round(self.pos.x, 0)), ' ')  # Clear previous position
        self.pos.y += self.speed  # Move asteroid down
        if self.pos.y < 28:
            if int(round(self.pos.x, 0)) == p1.pos.x and int(round(self.pos.y, 0)) == p1.pos.y:
                p1.lives -= 1  # Decrease player lives on collision
                stdscr.addstr(LINES // 2 - 13, 2, f"Lives: {p1.lives}")
                stdscr.addstr(LINES // 2 - 11, 2, f"Points: {p1.pts}")
                stdscr.refresh()
                return False  # Asteroid is removed on collision
            gameWin.addstr(int(round(self.pos.y, 0)), int(round(self.pos.x, 0)), self.symbol)  # Draw asteroid
        else:
            return False  # Asteroid is out of bounds
        return True  # Asteroid is still in bounds
class Player:
    def __init__(self, name, pts, x):
        self.name = name
        self.pts = pts
        self.lives = 3
        self.pos = Coordinate(x, 25)
        self.symbol = "A"
    def move_left(self, gameWin):
        gameWin.addstr(self.pos.y, self.pos.x, ' ')  # Clear previous position
        self.pos.x = max(1, self.pos.x - 1) # Update x position with boundary check
        gameWin.addstr(self.pos.y, self.pos.x, self.symbol)  # Draw player
    
    def move_right(self, gameWin):
        gameWin.addstr(self.pos.y, self.pos.x, ' ')  # Clear previous position
        self.pos.x = min(68, self.pos.x + 1) # Update x position with boundary check
        gameWin.addstr(self.pos.y, self.pos.x, self.symbol)  # Draw player
# Game function
def main(stdscr):
    # Cursor hide
    try:
        curses.curs_set(0)
        cursor_hidden = True
    except:
        cursor_hidden = False
    
    # Variables for game
    bullets = []
    asteroids = []
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
    p1 = Player("Player 1", 0, 35)
    gameWin = curses.newwin(30, 70, (LINES - 30) // 2, (COLS - 70) // 2)
    gameWin.border()
    gameWin.nodelay(True)
    gameWin.keypad(True)
    stdscr.refresh()
    gameWin.refresh()
    gameWin.addstr(p1.pos.y, p1.pos.x, p1.symbol)  # Draw first player
    # Static UI
    stdscr.addstr(LINES // 2 - 13, 2, f"Lives: {p1.lives}")
    stdscr.addstr(LINES // 2 - 11, 2, f"Points: {p1.pts}")
    stdscr.refresh()
    # Main game loop
    while True:
        # Get user input and update time
        last_update = time.monotonic()
        cur_key = gameWin.getch()
        if cur_key == ord('q'):
            break
        # Check death
        if p1.lives == 0:
            # Remove game window
            gameWin.clear()
            gameWin.refresh()
            del gameWin
            # Display game over screen
            stdscr.clear()
            for i in range(len(GAMEOVER)):
                stdscr.addstr(int(LINES // 2) + i - (len(GAMEOVER) // 2), int((COLS - len(GAMEOVER[i])) // 2), GAMEOVER[i])
            stdscr.addstr(LINES // 2 + (len(GAMEOVER) // 2) + 2, int((COLS - 22) // 2), f"Final Score: {p1.pts}", curses.A_BOLD)
            stdscr.addstr(LINES - 2, 2, "Press the ENTER key to end.", curses.A_ITALIC)
            stdscr.refresh()
            stdscr.nodelay(False)
            while True:
                end_key = stdscr.getch()
                if end_key == ord('\n') or end_key == ord('\r'):
                    break

            break
        # Update player position based on input
        if cur_key == curses.KEY_LEFT or cur_key == ord('a'):
            p1.move_left(gameWin)
        if cur_key == curses.KEY_RIGHT or cur_key == ord('d'):
            p1.move_right(gameWin)
        
        # Bullet stuff
        if cur_key == ord(' '):
            bullets.append(Bullet(p1))
        for bullet in bullets[:]:
            if not bullet.move(gameWin, asteroids):
                bullets.remove(bullet)

        # Asteroid stuff
        if random.randint(1, 50) == 1:
            asteroids.append(Asteroid())
        
        for asteroid in asteroids[:]:
            if not asteroid.move(gameWin, p1, stdscr, LINES):
                asteroids.remove(asteroid)
        
        # Bullet-Asteroid collision check
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                if bullet.pos.x == int(round(asteroid.pos.x, 0)) and bullet.pos.y == int(round(asteroid.pos.y, 0)):
                    gameWin.addstr(int(round(bullet.pos.y, 0)), int(round(bullet.pos.x, 0)), ' ')  # Clear bullet
                    gameWin.addstr(int(round(asteroid.pos.y, 0)), int(round(asteroid.pos.x, 0)), ' ')  # Clear asteroid
                    bullets.remove(bullet)
                    asteroids.remove(asteroid)
                    p1.pts += 1
                    stdscr.addstr(LINES // 2 - 13, 2, f"Lives: {p1.lives}    ")
                    stdscr.addstr(LINES // 2 - 11, 2, f"Points: {p1.pts}    ")
                    stdscr.refresh()
        
        # Refresh window
        if not cursor_hidden:
            gameWin.addstr(28, 68, " ") 
        gameWin.refresh()
        time.sleep(max(0, (1 / FPS) - (time.monotonic() - last_update)))

# Initialize game
curses.wrapper(main)