import tkinter as tk

class App(tk.Tk):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self, width=width, height=height, bg="white")
        self.canvas.pack()
        self.canvas.grid(row=0, column=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.canvas.config(cursor="pencil")

        self.stroke = 5
        self.pen_color = "#000000"
        self.currentPoint = [0, 0]
        self.prevPoint = [0, 0]
        self.points = []
        self.error = 0
        self.error_label = tk.Label(self, text="--")
        self.error_label.pack()

        # Event Binding
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.paint)
        self.canvas.bind("<Button-1>", self.paint)

    def set_error(self, error, radius):
        if radius > 100:
            self.error = error
            self.error_label.config(text="Score: " + str(min((1 - self.error) * 100, 100)) + "%")
        else:
            self.error_label.config(text="Circle too smol")

    def paint(self, event):

        x = event.x
        y = event.y

        self.currentPoint = [x, y]

        if self.prevPoint != [0, 0]:
            self.canvas.create_polygon(
                self.prevPoint[0],
                self.prevPoint[1],
                self.currentPoint[0],
                self.currentPoint[1],
                fill=self.pen_color,
                outline=self.pen_color,
                width=self.stroke,
            )
            self.points.append(self.currentPoint)

        self.prevPoint = self.currentPoint

        if event.type == "5":
            self.prevPoint = [0, 0]
            if (abs(self.currentPoint[0] - self.points[0][0])**2 + abs(self.currentPoint[1] - self.points[0][1])**2)**0.5 < 100:
                self.circle_eval()
            else: 
                self.error_label.config(text="Thas no circle")
                self.points = []
                self.after(200, lambda:self.canvas.delete("all"))
                
                

    def create_circle(self, point, r, **kwargs):
        x, y = point
        self.canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)

    def circle_eval(self):
        n = len(self.points)
        points_centre = (sum(map(lambda p : p[0], self.points))/n, sum(map(lambda p : p[1], self.points))/n)
        radii = tuple(map(lambda p: ((abs(p[0] - points_centre[0])**2 + abs(p[1] - points_centre[1])**2)**0.5), self.points))
        avg_radius = sum(radii)/n
        error = sum(map(lambda radius: abs(radius - avg_radius), radii))/(n**2)
        self.points = []
        self.create_circle(points_centre, avg_radius)
        self.after(1000, lambda:self.canvas.delete("all"))
        self.set_error(error, avg_radius)





x = App(600, 600)
x.mainloop()