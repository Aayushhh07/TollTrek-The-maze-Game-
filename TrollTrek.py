import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

# === Settings ===
NODE_RADIUS = 20
CANVAS_SIZE = 800
CAR_SIZE = 40

class TollTrekGame:
    def __init__(self, root):
        self.root = root
        self.root.title("TollTrek Maze v4 – Organic Graph Game")
        self.level = 1
        self.bg_path = "road_bg.png"
        self.car_path = "car.png"

        self.canvas = tk.Canvas(self.root, width=CANVAS_SIZE, height=CANVAS_SIZE)
        self.canvas.pack()

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()

        self.load_images()
        self.start_game()

    def load_images(self):
        bg = Image.open(self.bg_path).resize((CANVAS_SIZE, CANVAS_SIZE))
        self.bg_photo = ImageTk.PhotoImage(bg)
        car = Image.open(self.car_path).resize((CAR_SIZE, CAR_SIZE))
        self.car_photo = ImageTk.PhotoImage(car)

    def start_game(self):
        self.G = {}
        self.positions = {}
        self.blocked_edges = set()
        self.car_sprite = None
        self.path = []
        self.total_cost = 0
        self.current = 'A'
        self.destination = 'E'
        self.level_complete = False

        self.reset_level()

    def reset_level(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo)

        self.generate_graph(level=self.level)
        self.draw_edges()
        self.draw_nodes()

        cx, cy = self.positions[self.current]
        self.car_sprite = self.canvas.create_image(cx, cy, image=self.car_photo)

        self.path = [self.current]
        self.total_cost = 0
        self.update_ui()

    def generate_graph(self, level):
        node_count = 5 + level * 2
        self.G = {}
        self.positions = {}
        node_names = [chr(65 + i) for i in range(node_count)]

        for name in node_names:
            self.G[name] = []
            self.positions[name] = (
                random.randint(100, CANVAS_SIZE - 100),
                random.randint(100, CANVAS_SIZE - 100)
            )

        for u in node_names:
            others = [n for n in node_names if n != u]
            for _ in range(random.randint(1, 3)):
                v = random.choice(others)
                if v not in [x[0] for x in self.G[u]]:
                    cost = random.randint(3, 10)
                    self.G[u].append((v, cost))

        self.destination = node_names[-1]
        self.current = node_names[0]

        self.blocked_edges = set()
        for u in self.G:
            for v, _ in self.G[u]:
                if random.random() < 0.25:
                    self.blocked_edges.add((u, v))

    def draw_edges(self):
        for u in self.G:
            for v, cost in self.G[u]:
                x1, y1 = self.positions[u]
                x2, y2 = self.positions[v]
                color = 'red' if (u, v) in self.blocked_edges else 'white'
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=3)
                mx, my = (x1 + x2) // 2, (y1 + y2) // 2
                label = f"{cost}"
                self.canvas.create_text(mx, my, text=label, fill="yellow", font=("Arial", 10, "bold"))

    def draw_nodes(self):
        for node, (x, y) in self.positions.items():
            self.canvas.create_oval(x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS, fill='lightblue')
            self.canvas.create_text(x, y, text=node, font=("Arial", 12, "bold"))

    def draw_ui(self):
        self.update_ui()

    def update_ui(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        tk.Label(self.button_frame, text=f"🚗 Current: {self.current}", font=("Arial", 12)).pack()

        neighbors = [v for v, _ in self.G[self.current]]
        for v in neighbors:
            state = tk.DISABLED if (self.current, v) in self.blocked_edges else tk.NORMAL
            tk.Button(
                self.button_frame,
                text=f"Move to {v}",
                state=state,
                command=lambda n=v: self.move_car(n)
            ).pack(pady=2)

    def move_car(self, next_node):
        if (self.current, next_node) in self.blocked_edges:
            messagebox.showwarning("Blocked", "That road is blocked!")
            return

        for v, cost in self.G[self.current]:
            if v == next_node:
                self.total_cost += cost

        self.path.append(next_node)
        self.animate_movement(self.current, next_node)
        self.current = next_node

        if self.current == self.destination:
            self.level_complete = True
            messagebox.showinfo("🎉 Level Complete", f"Path: {' → '.join(self.path)}\nTotal Toll Cost: {self.total_cost}")
            self.level += 1
            self.reset_level()
        else:
            self.update_ui()

    def animate_movement(self, start, end, steps=10):
        x1, y1 = self.positions[start]
        x2, y2 = self.positions[end]
        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps
        for _ in range(steps):
            self.canvas.move(self.car_sprite, dx, dy)
            self.canvas.update()
            self.canvas.after(50)

# === Run the Game ===
if __name__ == "__main__":
    root = tk.Tk()
    game = TollTrekGame(root)
    root.mainloop()
