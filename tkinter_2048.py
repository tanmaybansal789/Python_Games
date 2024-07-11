from random import choice
import tkinter as tk
from tkinter.font import Font
from tkinter.simpledialog import askstring

#pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonboosted.org pip <LIBRARY>

class Tile:
    TILE_SIZE = 100
    COLOUR_DICT = {
        2: "#EEE4DA",
        4: "#EDE0C8",
        8: "#F2B179",
        16: "#F59563",
        32: "#F67C5F",
        64: "#F65E3B",
        128: "#EDCF72",
        256: "#EDCC61",
        512: "#EDC850",
        1024: "#EDC53F",
        2048: "#EDC22E"
    }
    def __init__(self, canvas, root, x_pos, y_pos, value):
        self.canvas = canvas
        self.root = root
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.value = value
        self.rect_id = None
        self.is_moving = False
        self.smooth_show()

    def show(self):
        x1 = self.x_pos * self.TILE_SIZE
        y1 = self.y_pos * self.TILE_SIZE
        x2 = x1 + self.TILE_SIZE
        y2 = y1 + self.TILE_SIZE
        self.rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.COLOUR_DICT.get(self.value, "#EEE4DA"), outline="#CFBCA3", width=5)
        self.text_id = self.canvas.create_text(x1 + self.TILE_SIZE/2, y1 + self.TILE_SIZE/2, text=str(self.value), font=Font(family="Clear Sans", size=Tile.TILE_SIZE//5, weight="bold"), fill="black")

    def smooth_show(self, iter_size=5, i=1):
        x1 = self.x_pos * self.TILE_SIZE + ((self.TILE_SIZE//2) - i*iter_size)
        y1 = self.y_pos * self.TILE_SIZE + ((self.TILE_SIZE//2) - i*iter_size)
        x2 = self.x_pos * self.TILE_SIZE + ((self.TILE_SIZE//2) + i*iter_size)
        y2 = self.y_pos * self.TILE_SIZE + ((self.TILE_SIZE//2) + i*iter_size)
        if i == 1:
            self.rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.COLOUR_DICT.get(self.value, "#EEE4DA"), outline="#CFBCA3", width=5)
            self.text_id = self.canvas.create_text(x1 + iter_size, y1 + iter_size, text=str(self.value), font=Font(family="Clear Sans", size=Tile.TILE_SIZE//5, weight="bold"), fill="black")
        else: self.canvas.coords(self.rect_id, x1, y1, x2, y2)           
        if ((self.TILE_SIZE//2) - i*iter_size) != 0: 
            self.root.after(5, lambda:self.smooth_show(iter_size, i + 1))

    def move_horizontal(self, new_x_pos, iter_dist, i = 1):
        self.is_moving = True
        dir_move = 1 if (new_x_pos - self.x_pos) >= 0 else -1
        if i%(self.TILE_SIZE//iter_dist) == 0: self.x_pos += dir_move
        self.canvas.move(self.rect_id, iter_dist * dir_move, 0)
        self.canvas.move(self.text_id, iter_dist * dir_move, 0)
        if self.x_pos == new_x_pos: self.is_moving = False
        else: self.root.after(5, lambda: self.move_horizontal(new_x_pos, iter_dist, i + 1))
    
    def move_vertical(self, new_y_pos, iter_dist, i = 1):
        self.is_moving = True
        dir_move = 1 if (new_y_pos - self.y_pos) >= 0 else -1
        if i%(self.TILE_SIZE//iter_dist) == 0: self.y_pos += dir_move
        self.canvas.move(self.rect_id, 0, iter_dist * dir_move)
        self.canvas.move(self.text_id, 0, iter_dist * dir_move)
        if self.y_pos == new_y_pos: self.is_moving = False
        else: self.root.after(5, lambda: self.move_vertical(new_y_pos, iter_dist, i + 1))

    def move_coords(self, new_x_pos, new_y_pos):
        self.canvas.move(self.rect_id, (new_x_pos - self.x_pos)*self.TILE_SIZE, (new_y_pos - self.y_pos)*self.TILE_SIZE)
        self.canvas.move(self.text_id, (new_x_pos - self.x_pos)*self.TILE_SIZE, (new_y_pos - self.y_pos)*self.TILE_SIZE)
    
    def hide(self):
        self.canvas.delete(self.rect_id)
        self.canvas.delete(self.text_id)

    def delayed_hide(self, delay):
        self.root.after(delay, self.hide)
    
    def double_value(self):
        self.value *= 2
        self.hide(); self.show()

class Board:
    def __init__(self, canvas, root, starting_board):
        self.canvas = canvas
        self.root = root
        self.tiles = {(i, j): Tile(canvas, root, i, j, starting_board[j][i]) for i in range(len(starting_board[0])) for j in range(len(starting_board)) if starting_board[j][i] != 0}
        self.board_x = len(starting_board[0])
        self.board_y = len(starting_board)
        self.animation_playing = False
        self.horiz_animation_buffer = 120 * board_x + 100
        self.vert_animation_buffer = 120 * board_y + 100
        self.game_over = False
        self.score = 0

    def get_line(self, i, axis): #0, 1 -> ROW, COL
        if axis: return [self.tiles[(i, j)].value if (i, j) in self.tiles else 0 for j in range(self.board_y)]
        else: return [self.tiles[(j, i)].value if (j, i) in self.tiles else 0 for j in range(self.board_x)]

    def get_updated_row(self, row, dir): # 0 = L, 1 = R
        z_row =  [(row[i], i) for i in range(len(row)) if row[i] != 0]
        pos_row = []
        i = len(z_row) - 1 if dir else 0
        step = -1 if dir else 1
        end_value = 0 if dir else len(z_row) - 1
        while -1 < i < len(z_row):
            if end_value != i and z_row[i][0] == z_row[i + step][0]:
                pos_row.insert(0, (z_row[i][1], z_row[i + step][1])) if dir else pos_row.append((z_row[i][1], z_row[i + step][1])) 
                i += 2 * step
            else:
                pos_row.insert(0, (z_row[i][1], None)) if dir else pos_row.append((z_row[i][1], None)) 
                i += step
        return [(None, None)] * (len(row) - len(pos_row)) + pos_row if dir else pos_row + [(None, None)] * (len(row) - len(pos_row))
    
    def move_tile_horiz(self, pos_x, pos_y, new_pos_x):
        if (new_pos_x, pos_y) in self.tiles:
            self.tiles[(pos_x, pos_y)].double_value()
            self.score += self.tiles[(pos_x, pos_y)].value
            self.tiles[(new_pos_x, pos_y)].delayed_hide(self.horiz_animation_buffer)
        self.tiles[(new_pos_x, pos_y)] = self.tiles.pop((pos_x, pos_y))
        self.tiles[(new_pos_x, pos_y)].move_horizontal(new_pos_x, Tile.TILE_SIZE//5)
    
    def move_tile_vert(self, pos_x, pos_y, new_pos_y):
        if (pos_x, new_pos_y) in self.tiles:
            self.tiles[(pos_x, pos_y)].double_value()
            self.score += self.tiles[(pos_x, pos_y)].value
            self.tiles[(pos_x, new_pos_y)].delayed_hide(self.vert_animation_buffer)
        self.tiles[(pos_x, new_pos_y)] = self.tiles.pop((pos_x, pos_y))
        self.tiles[(pos_x, new_pos_y)].move_vertical(new_pos_y, Tile.TILE_SIZE//5)

    def reset_animation_flag(self):
        self.check_game_over()
        self.animation_playing = False

    def move_left(self):
        if self.animation_playing:
            return
        self.animation_playing = True
        old_board = self.get_board_state()
        for y in range(self.board_y):
            row_pos = self.get_updated_row(self.get_line(y, 0), 0)
            for x in range(self.board_x):
                if row_pos[x][0] not in (None, x): self.move_tile_horiz(row_pos[x][0], y, x)
                if row_pos[x][1] not in (None, x): self.move_tile_horiz(row_pos[x][1], y, x)
        if old_board != self.get_board_state(): 
            self.root.after(100, lambda: self.random_tile(2))
        self.root.after(self.horiz_animation_buffer, lambda: self.reset_animation_flag())
        update_score()

    
    def move_right(self):
        if self.animation_playing:
            return
        self.animation_playing = True
        old_board = self.get_board_state()
        for y in range(self.board_y):
            row_pos = self.get_updated_row(self.get_line(y, 0), 1)
            for x in range(self.board_x - 1, 0, -1):
                if row_pos[x][0] not in (None, x): self.move_tile_horiz(row_pos[x][0], y, x)
                if row_pos[x][1] not in (None, x): self.move_tile_horiz(row_pos[x][1], y, x)
        if old_board != self.get_board_state(): 
            self.root.after(100, lambda: self.random_tile(2))
        self.root.after(self.horiz_animation_buffer, lambda: self.reset_animation_flag())
        update_score()

    def move_up(self):
        if self.animation_playing:
            return
        self.animation_playing = True
        old_board = self.get_board_state()
        for x in range(self.board_x):
            col_pos = self.get_updated_row(self.get_line(x, 1), 0)
            for y in range(self.board_y):
                if col_pos[y][0] not in (None, y): self.move_tile_vert(x, col_pos[y][0], y)
                if col_pos[y][1] not in (None, y): self.move_tile_vert(x, col_pos[y][1], y)
        if old_board != self.get_board_state(): 
            self.root.after(100, lambda: self.random_tile(2))
        self.root.after(self.vert_animation_buffer, lambda: self.reset_animation_flag())
        update_score()

    
    def move_down(self):
        if self.animation_playing:
            return
        self.animation_playing = True
        old_board = self.get_board_state()
        for x in range(self.board_x):
            col_pos = self.get_updated_row(self.get_line(x, 1), 1)
            for y in range(self.board_y - 1, 0, -1):
                if col_pos[y][0] not in (None, y): self.move_tile_vert(x, col_pos[y][0], y)
                if col_pos[y][1] not in (None, y): self.move_tile_vert(x, col_pos[y][1], y)
        if old_board != self.get_board_state(): 
            self.root.after(200, lambda: self.random_tile(2))
        self.root.after(self.vert_animation_buffer, lambda: self.reset_animation_flag())
        update_score()

    def get_board_state(self):
        board_state = []
        for y in range(self.board_y):
            board_state.append(self.get_line(y, 0))
        return board_state
    
    def random_tile(self, value):
        possible_positions = [(x, y) for x in range(self.board_x) for y in range(self.board_y) if (x, y) not in self.tiles.keys()]
        if possible_positions:
            x, y = choice(possible_positions)
            self.tiles[(x, y)] = Tile(self.canvas, self.root, x, y, value)

    def check_game_over(self):
        for y in range(self.board_y):
            row = self.get_line(y, 0)
            for x in range(self.board_x):
                if (x != self.board_x - 1 and row[x] == row[x + 1]) or row[x] == 0: return
        for x in range(self.board_x):     
            col = self.get_line(x, 1)
            for y in range(self.board_y):
                if (y != self.board_y - 1 and col[y] == col[y + 1]) or col[y] == 0: return
        self.end()
    
    def end(self): 
        if not self.game_over:
            tk.Label(self.root, text="GAME OVER", font=Font(family="Clear Sans", size=Tile.TILE_SIZE//5, weight="bold")).pack()
            self.root.after(2000, lambda: self.root.destroy())
        self.game_over = True


def on_drag(event):
    global start_x, start_y
    global action_triggered
    current_x, current_y = event.x, event.y
    if start_x is not None and start_y is not None:
        distance_x = current_x - start_x
        distance_y = current_y - start_y
        if abs(distance_x) >= Tile.TILE_SIZE and not action_triggered:
            if distance_x > 0:
                game_board.move_right()
            else:
                game_board.move_left()
            action_triggered = True
        elif abs(distance_y) >= Tile.TILE_SIZE and not action_triggered:
            if distance_y > 0:
                game_board.move_down()
            else:
                game_board.move_up()
            action_triggered = True
    else:
        start_x, start_y = current_x, current_y

def on_release(event):
    global start_x, start_y
    global action_triggered
    start_x, start_y = None, None
    action_triggered = False

def update_score():
    score_label.config(text="Score: " + str(game_board.score))


start_x, start_y = None, None
action_triggered = False

root = tk.Tk()
root.title("2048 - By Tanmay Bansal")
    # Example usage:
board_x, board_y = map(int, askstring('Size', 'What size should the grid be? Say in terms of X<space>Y').split())

canvas = tk.Canvas(root, width=board_x*Tile.TILE_SIZE, height=board_y*Tile.TILE_SIZE, bg="#DBCEBD")
canvas.pack()

for i in range(board_x + 1):
    canvas.create_line(i * Tile.TILE_SIZE, 0, i * Tile.TILE_SIZE, board_y * Tile.TILE_SIZE, fill="#CFBCA3", width=5)
for i in range(board_y + 1):
    canvas.create_line(0, i * Tile.TILE_SIZE, board_x * Tile.TILE_SIZE, i * Tile.TILE_SIZE, fill="#CFBCA3", width=5)

game_board = Board(canvas, root, [[0]*board_x]*board_y)
game_board.random_tile(2); game_board.random_tile(2)

score_label = tk.Label(root, text="Score: " + str(game_board.score), font=Font(family="Clear Sans", size=Tile.TILE_SIZE//5, weight="bold"))
score_label.pack()

root.bind("<Left>", lambda x:game_board.move_left())
root.bind("<Right>", lambda x:game_board.move_right())
root.bind("<Up>", lambda x:game_board.move_up())
root.bind("<Down>", lambda x:game_board.move_down())

canvas.bind("<B1-Motion>", on_drag)
canvas.bind("<ButtonRelease-1>", on_release)



root.mainloop()