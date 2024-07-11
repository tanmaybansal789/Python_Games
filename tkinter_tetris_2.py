import tkinter as tk
from random import choice

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 30
UPDATE_SPEED = 250

SHAPES = [
    [[0, 0, 0, 0],
     [1, 1, 1, 1],
     [0, 0, 0, 0],
     [0, 0, 0, 0]],

    [[2, 0, 0],
     [2, 2, 2],
     [0, 0, 0]],

    [[0, 0, 3],
     [3, 3, 3],
     [0, 0, 0]],

    [[4, 4],
     [4, 4]],

    [[0, 5, 5],
     [5, 5, 0],
     [0, 0, 0]],

    [[0, 6, 0],
     [6, 6, 6],
     [0, 0, 0]],

    [[7, 7, 0],
     [0, 7, 7],
     [0, 0, 0]]
]

COLORS = [('#00FFFF','#00BFAF'), ('#0000FF', '#0000B0'), ('#FFA500', '#C27E00'), ('#FFFF00', '#CFCF00'), ('#00FF00', '#00B800'), ('#A020F0', '#7819B3'), ('#FF0000', '#BD0000')]

class Tetris:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tetris")
        self.canvas = tk.Canvas(self.root, width=BLOCK_SIZE * BOARD_WIDTH, height=BLOCK_SIZE * BOARD_HEIGHT, bg="black")
        self.canvas.pack()
        self.score_label = tk.Label(self.root, text="Score: 0", fg="white", bg="black", font=("Arial", 16))
        self.score_label.pack()
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.bag = []
        self.current_shape = self.new_shape()
        self.current_x = BOARD_WIDTH // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0
        self.score = 0
        self.root.bind("<KeyPress>", self.key_pressed)
        self.update()

        self.root.mainloop()
    
    def rotate_shape(self, dir):
        rotated_shape = [list(row)[::-1] for row in zip(*self.current_shape)] if dir else [list(row) for row in zip(*self.current_shape)][::-1]
        if self.is_valid_position(rotated_shape, self.current_x, self.current_y):
            self.current_shape = rotated_shape
            self.draw_board()
            self.draw_shape()


    def new_shape(self):
        if len(self.bag) == 0: self.bag = [1, 2, 3, 4, 5, 6, 7]
        shape = choice(self.bag)
        self.bag.remove(shape)
        return SHAPES[shape - 1]

    def draw_board(self):
        self.canvas.delete("all")
        for y, row in enumerate(self.board):
            for x, val in enumerate(row):
                if val:
                    self.canvas.create_polygon(x * BLOCK_SIZE, y * BLOCK_SIZE,
                                            x * BLOCK_SIZE + BLOCK_SIZE, y * BLOCK_SIZE,
                                            x * BLOCK_SIZE + BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE,
                                            fill=COLORS[val - 1][1], outline="")
                    self.canvas.create_polygon(x * BLOCK_SIZE, y * BLOCK_SIZE,
                                            x * BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE,
                                            x * BLOCK_SIZE + BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE,
                                            fill=COLORS[val - 1][0], outline="")
                else:
                    self.canvas.create_polygon(x * BLOCK_SIZE, y * BLOCK_SIZE,
                                            x * BLOCK_SIZE + BLOCK_SIZE, y * BLOCK_SIZE,
                                            x * BLOCK_SIZE + BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE,
                                            fill="#1c1c1c", outline="")
                    self.canvas.create_polygon(x * BLOCK_SIZE, y * BLOCK_SIZE,
                                            x * BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE,
                                            x * BLOCK_SIZE + BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE,
                                            fill="#1a1a1a", outline="")


    def draw_shape(self):
        for y, row in enumerate(self.current_shape):
            for x, val in enumerate(row):
                if val:
                    self.canvas.create_polygon((self.current_x + x) * BLOCK_SIZE, (self.current_y + y) * BLOCK_SIZE,
                                            (self.current_x + x + 1) * BLOCK_SIZE, (self.current_y + y) * BLOCK_SIZE,
                                            (self.current_x + x + 1) * BLOCK_SIZE, (self.current_y + y + 1) * BLOCK_SIZE,
                                            fill=COLORS[val - 1][1], outline="")
                    self.canvas.create_polygon((self.current_x + x) * BLOCK_SIZE, (self.current_y + y) * BLOCK_SIZE,
                                            (self.current_x + x) * BLOCK_SIZE, (self.current_y + y + 1) * BLOCK_SIZE,
                                            (self.current_x + x + 1) * BLOCK_SIZE, (self.current_y + y + 1) * BLOCK_SIZE,
                                            fill=COLORS[val - 1][0], outline="")
                

    def key_pressed(self, event):
        if event.keysym == 'Left':
            self.move(-1)
        elif event.keysym == 'Right':
            self.move(1)
        elif event.keysym == 'Down':
            self.drop()
        elif event.keysym == 'Up':
            self.rotate_shape(0)

    def move(self, dx):
        new_x = self.current_x + dx
        if self.is_valid_position(self.current_shape, new_x, self.current_y):
            self.current_x = new_x
            self.draw_board()
            self.draw_shape()

    def drop(self):
        self.current_y += 1
        if not self.is_valid_position(self.current_shape, self.current_x, self.current_y):
            self.current_y -= 1
            self.merge_shape()
            self.clear_lines()
            self.current_shape = self.new_shape()
            self.current_x = BOARD_WIDTH // 2 - len(self.current_shape[0]) // 2
            self.current_y = 0
            if not self.is_valid_position(self.current_shape, self.current_x, self.current_y):
                self.game_over()
        self.draw_board()
        self.draw_shape()

    def is_valid_position(self, shape, x, y):
        for y_idx, row in enumerate(shape):
            for x_idx, val in enumerate(row):
                if val != 0:
                    board_x = x + x_idx
                    board_y = y + y_idx
                    if not (0 <= board_x < BOARD_WIDTH and 0 <= board_y < BOARD_HEIGHT) or self.board[board_y][board_x] != 0:
                        return False
        return True

    def merge_shape(self):
        for y, row in enumerate(self.current_shape):
            for x, val in enumerate(row):
                if val != 0:
                    self.board[self.current_y + y][self.current_x + x] = val

    def clear_lines(self):
        lines_cleared = 0
        for y in range(BOARD_HEIGHT):
            if all(self.board[y]):
                del self.board[y]
                self.board.insert(0, [0] * BOARD_WIDTH)
                lines_cleared += 1
        self.score += lines_cleared * 100

    def game_over(self):
        self.root.quit()
        print("Game Over! Score:", self.score)

    def update(self):
        self.drop()
        self.update_score_label() 
        self.root.after(UPDATE_SPEED, self.update)
    
    def update_score_label(self):
        self.score_label.config(text=f"Score: {self.score}")

if __name__ == "__main__":
    game = Tetris()