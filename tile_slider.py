import tkinter as tk
from tkinter.font import Font
from colorsys import hsv_to_rgb

from collections import deque
from heapq import heappop, heappush

from math import cos, pi
from random import choice
from time import time


TILE_SIZE = 100

def xfrange(start, stop, step = TILE_SIZE // 5):
    x = start
    if start > stop:
        while x > stop:
            yield x
            x -= step
    else:
        while x < stop:
            yield x
            x += step

def inv_quad_xfrange(start, stop, step = TILE_SIZE // 5, step_step = 2.5):
    x = start
    if start > stop:
        while x > stop:
            yield x
            x -= step
            step -= step_step
            step = max(step, 1)
    else:
        while x < stop:
            yield x
            x += step
            step -= step_step
            step = max(step, 1)

def cos_interp(a, b, t_s=0.2):
    t = 0
    while t <= 1:
        yield a + (1 - cos(pi * t)) / 2 * (b - a)
        t += t_s

def int_to_hex_color(val, max_val=100):
    normalized_val = val / max_val
    hue = normalized_val
    r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    return f"#{r:02X}{g:02X}{b:02X}"

class Tile():
    def __init__(self, root, canvas, xpos, ypos, value, size = TILE_SIZE):
        self.root = root
        self.canvas = canvas
        self.xpos = xpos
        self.ypos = ypos
        self.value = value
        self.size = size
        self.current_path = deque()
        self.rect_id = None
        self.text_id = None
        self.shown = False

        self.show()

    def move(self, axis, distance):
        # dir: 0 => horizontal, 1 => vertical
        scaled_xpos = self.xpos * self.size
        scaled_ypos = self.ypos * self.size

        if axis == 0:  
            stop_scaled_xpos = scaled_xpos + distance * self.size
            for lerp_scaled_xpos in inv_quad_xfrange(scaled_xpos, stop_scaled_xpos):
                self.current_path.append((lerp_scaled_xpos, scaled_ypos))
            self.current_path.append((stop_scaled_xpos, scaled_ypos))
            self.xpos += distance

        else:
            stop_scaled_ypos = scaled_ypos + distance * self.size
            for lerp_scaled_ypos in inv_quad_xfrange(scaled_ypos, stop_scaled_ypos):
                self.current_path.append((scaled_xpos, lerp_scaled_ypos))
            self.current_path.append((scaled_xpos, stop_scaled_ypos))
            self.ypos += distance
        
        self.move_start = time()

    def update(self):
        if not self.current_path: return
        new_xpos, new_ypos = self.current_path.popleft()
        self.canvas.moveto(self.rect_id, new_xpos, new_ypos)
        self.canvas.coords(self.text_id, new_xpos + self.size // 2, new_ypos + self.size // 2)

    def hide(self):
        if not self.shown: return
        self.canvas.delete(self.rect_id)
        self.canvas.delete(self.text_id)
        self.shown = False

    def show(self):
        if self.shown: return
        x1, y1 = self.xpos * self.size, self.ypos * self.size
        x2, y2 = x1 + self.size, y1 + self.size
        self.rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=int_to_hex_color(self.value, 75), width=0)
        self.text_id = self.canvas.create_text(x1 + self.size // 2, y1 + self.size // 2, text=str(self.value), font=Font(family="Clear Sans", size=TILE_SIZE//5, weight="bold"), fill="black")
        self.shown = True

def manhattan_distance(state, goal):
    distance = 0
    rows = len(state)
    cols = len(state[0])
    positions = {value: (row, col) for row in range(rows) for col in range(cols) for value in [goal[row][col]]}
    for i in range(rows):
        for j in range(cols):
            if state[i][j] != 0:
                value = state[i][j]
                target_x, target_y = positions[value]
                distance += abs(target_x - i) + abs(target_y - j)
    return distance

def get_neighbors(state):
    rows = len(state)
    cols = len(state[0])
    x = y = -1
    for i in range(rows):
        for j in range(cols):
            if state[i][j] == 0:
                x, y = i, j
                break

    neighbors = []
    directions = [(0, 1, 'left'), (0, -1, 'right'), (1, 0, 'up'), (-1, 0, 'down')]
    for dx, dy, direction in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < rows and 0 <= ny < cols:
            new_state = [list(row) for row in state]  # Create a new state as a list of lists
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            neighbors.append((tuple(map(tuple, new_state)), direction))  # Convert the new state to a tuple of tuples
    return neighbors


def greedy_best_first_search(initial_state, goal):
    initial_state_tuple = tuple(map(tuple, initial_state))
    goal_tuple = tuple(map(tuple, goal))
    open_set = []
    heappush(open_set, (manhattan_distance(initial_state, goal), initial_state_tuple, []))
    seen = set()

    while open_set:
        _, current, path = heappop(open_set)

        if current == goal_tuple:
            return path

        if current in seen:
            continue

        seen.add(current)

        for neighbor, direction in get_neighbors(current):
            if neighbor not in seen:
                new_path = path + [(neighbor, direction)]
                heappush(open_set, (manhattan_distance(neighbor, goal), neighbor, new_path))

    return None

def a_star(initial_state, goal):
    open_set = []
    heappush(open_set, (manhattan_distance(initial_state, goal), 0, initial_state, []))
    seen = {}

    while open_set:
        _, cost, current, path = heappop(open_set)

        if current == goal:
            return path

        if tuple(map(tuple, current)) in seen and seen[tuple(map(tuple, current))] <= cost:
            continue

        seen[tuple(map(tuple, current))] = cost

        for neighbor, direction in get_neighbors(current):
            new_path = path + [(neighbor, direction)]
            heappush(open_set, (cost + 1 + manhattan_distance(neighbor, goal), cost + 1, neighbor, new_path))

    return None

class Board(tk.Tk):
    def __init__(self, width, height):
        super().__init__()
        self.canvas = tk.Canvas(self, width=width*TILE_SIZE, height=height*TILE_SIZE, bg="#000000")
        self.width = width
        self.height = height
        self.tiles = dict()
        for xpos in range(width):
            for ypos in range(height):
                self.tiles[(xpos, ypos)] = Tile(self, self.canvas, xpos, ypos, ypos * width + xpos + 1)

        self.empty_pos = (width - 1, height - 1)
        self.tiles[self.empty_pos].hide()
        self.tiles.pop(self.empty_pos)

        self.canvas.pack()

        # Frame for the buttons and timer
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Timer Label
        self.timer_label = tk.Label(self.button_frame, text="", font=Font(family="Clear Sans", size=10, weight="bold"))
        self.timer_label.pack(side="right")

        # Control Buttons
        self.scramble_button = tk.Button(self.button_frame, text="Scramble", command=self.scramble)
        self.scramble_button.pack(side="left")

        self.solve_button = tk.Button(self.button_frame, text="Solve", command=self.update_and_execute_solution)
        self.solve_button.pack(side="left")

        self.timer_button = tk.Button(self.button_frame, text="Start Timer", command=self.start_timer)
        self.timer_button.pack(side="left")

        self.solution_path = []
        self.prev_move = (0, -1)
        self.scramble_move_counts = {
            (0, -1) : 0,
            (0, 1) : 0,
            (1, -1) : 0,
            (1, 1) : 0
        }

        self.valid_moves = set()
        self.update_valid_moves()

        self.start_time = None
        self.move_start_time = time()
        self.anim_buffer = 0.05

        self.update()

    def update(self):
        for tile in self.tiles.values():
            tile.update()
            
        self.after(5, self.update)
        if self.start_time: self.timer_label.config(text="Elapsed time: {:.2f}s".format(time() - self.start_time))

    def update_valid_moves(self):
        self.valid_moves = set()
        empty_xpos, empty_ypos = self.empty_pos

        if empty_xpos > 0:
            self.valid_moves.add((0, 1))
        if empty_xpos < self.width - 1:
            self.valid_moves.add((0, -1))
        if empty_ypos > 0:
            self.valid_moves.add((1, 1))
        if empty_ypos < self.height - 1:
            self.valid_moves.add((1, -1))


    def move(self, axis, dir):
        if time() - self.move_start_time < self.anim_buffer or (axis, dir) not in self.valid_moves: return
        empty_xpos, empty_ypos = self.empty_pos
        if axis == 0: pos = (empty_xpos - dir, empty_ypos)
        else: pos = (empty_xpos, empty_ypos - dir)
        self.tiles[pos].move(axis, dir)
        self.tiles[self.empty_pos] = self.tiles.pop(pos)
        self.empty_pos = pos
        self.prev_move = (axis, dir)
        self.update_valid_moves()
        if self.get_board() == self.get_goal_board(): 
            if self.start_time: self.timer_label.config(text="You've won in {:.2f}s!".format(time() - self.start_time))
            self.start_time = None
        self.move_start_time = time()



    def scramble(self, i=0):
        undo_move = (self.prev_move[0], -self.prev_move[1])

        move_choices = tuple(move for move in ((0, -1), (0, 1), (1, -1), (1, 1)) 
                        if move in self.valid_moves and move != undo_move)
                
        self.move(*choice(move_choices))

        if i < self.width * self.height * 8: self.after(50, lambda: self.scramble(i + 1))
        else: self.start_time = time()

    def start_timer(self):
        self.start_time = time()

    def get_board(self):
        board_state = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for (xpos, ypos), tile in self.tiles.items():
            board_state[ypos][xpos] = tile.value
        return board_state
    
    def get_goal_board(self):
        goal_board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for xpos in range(self.width):
            for ypos in range(self.height):
                goal_board[ypos][xpos] = ypos * self.width + xpos + 1
        goal_board[self.height - 1][self.width - 1] = 0
        return goal_board
    
    def update_solution(self):
        initial_state = self.get_board()
        goal_state = self.get_goal_board()
        self.solution_path = greedy_best_first_search(initial_state, goal_state)
        if self.solution_path:
            print("Solution found in", len(self.solution_path), "moves.")
            #for step, (state, direction) in enumerate(self.solution_path, 1):
            #print("Step", step, ":", direction)
            #for row in state:
            #print(row)
        else:
            print("Already at solved state")

    def execute_solution(self):
        if not self.solution_path: return
        state, direction = self.solution_path.pop(0)
        dir_to_move_map = {
            "left" : (0, -1),
            "right" : (0, 1),
            "up" : (1, -1),
            "down" : (1, 1)
        }
        self.move(*dir_to_move_map[direction])
        self.after(60, self.execute_solution)

    def update_and_execute_solution(self):
        self.update_solution()
        self.execute_solution()

def on_drag(event):
    global start_x, start_y
    global action_triggered
    current_x, current_y = event.x, event.y
    if start_x is not None and start_y is not None:
        distance_x = current_x - start_x
        distance_y = current_y - start_y
        if abs(distance_x) >= TILE_SIZE and not action_triggered:
            if distance_x > 0:
                game_board.move(0, 1)
            else:
                game_board.move(0, -1)
            action_triggered = True
        elif abs(distance_y) >= TILE_SIZE and not action_triggered:
            if distance_y > 0:
                game_board.move(1, 1)
            else:
                game_board.move(1, -1)
            action_triggered = True
    else:
        start_x, start_y = current_x, current_y

def on_release(event):
    global start_x, start_y
    global action_triggered
    start_x, start_y = None, None
    action_triggered = False


start_x, start_y, action_triggered = 0, 0, False

game_board = Board(5, 5)

def update_and_execute_solution():
    game_board.update_solution()
    game_board.execute_solution()


game_board.bind("<Left>", lambda _ : game_board.move(0, -1))
game_board.bind("<Right>", lambda _ : game_board.move(0, 1))
game_board.bind("<Up>", lambda _ : game_board.move(1, -1))
game_board.bind("<Down>", lambda _ : game_board.move(1, 1))

game_board.canvas.bind("<B1-Motion>", on_drag)
game_board.canvas.bind("<ButtonRelease-1>", on_release)

game_board.mainloop()
