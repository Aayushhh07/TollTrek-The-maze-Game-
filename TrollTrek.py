import tkinter as tk
from tkinter import messagebox
import random
from collections import deque
import heapq

# === Game Settings ===
GRID_SIZE = 9
CELL_SIZE = 60
STARTING_MONEY = 200
MAX_LEVELS = 5
MIN_TOLLS_TO_CROSS = 2
GAMES_NEEDED_FOR_HINTS = 2

# Emoji Assets
WALL_EMOJI = "🧱"
CAR_EMOJI = "🚗"
DESTINATION_EMOJI = "🏁"
HINT_EMOJI = "💡"
TOLL_EMOJIS = ["🏰", "💰", "🏦", "⛽", "🛣️"] 
WEATHERS = {
    '☀️': {"multiplier": 1.0, "message": "Normal toll rates"},
    '🌧️': {"multiplier": 1.2, "message": "20% higher tolls"},
    '🌫️': {"multiplier": 1.5, "message": "50% higher tolls"},
    '❄️': {"multiplier": 1.3, "message": "30% higher tolls"}
}

class TollTrekMaze:
    def __init__(self, root):
        self.root = root
        self.root.title("TollTrek Maze Pro - Guaranteed Path")
        
        # Game state
        self.level = 1
        self.money = STARTING_MONEY
        self.total_cost = 0
        self.player_pos = (0, 0)
        self.destination = (GRID_SIZE-1, GRID_SIZE-1)
        self.walls = set()
        self.tolls = {}
        self.path = []
        self.game_count = 0
        self.show_hints = False
        self.optimal_path = []
        self.current_hint_index = 0
        
        # UI Setup
        self.setup_ui()
        self.start_level()
        
        # Key bindings
        self.root.bind("<Up>", lambda e: self.move(-1, 0))
        self.root.bind("<Down>", lambda e: self.move(1, 0))
        self.root.bind("<Left>", lambda e: self.move(0, -1))
        self.root.bind("<Right>", lambda e: self.move(0, 1))
        self.root.bind("h", lambda e: self.show_next_hint())
        
    def setup_ui(self):
        """Initialize all UI components"""
        self.canvas = tk.Canvas(
            self.root, 
            width=GRID_SIZE*CELL_SIZE, 
            height=GRID_SIZE*CELL_SIZE,
            bg="#f0f0f0"
        )
        self.canvas.pack(pady=10)
        
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.level_label = tk.Label(self.info_frame, text="", font=("Arial", 12))
        self.level_label.pack(side=tk.LEFT)
        
        self.money_label = tk.Label(self.info_frame, text="", font=("Arial", 12))
        self.money_label.pack(side=tk.LEFT, padx=20)
        
        self.weather_label = tk.Label(self.info_frame, text="", font=("Arial", 12))
        self.weather_label.pack(side=tk.RIGHT)
        
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(pady=5)
        
        tk.Button(self.controls_frame, text="Restart Level", command=self.start_level).pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls_frame, text="Hint (H)", command=self.show_next_hint).pack(side=tk.LEFT, padx=5)
        tk.Button(self.controls_frame, text="Optimal Path", command=self.show_full_optimal_path).pack(side=tk.LEFT, padx=5)
    
    def start_level(self):
        """Initialize a new level"""
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.walls = set()
        self.tolls = {}
        self.player_pos = (0, 0)
        self.path = [self.player_pos]
        self.current_hint_index = 0
        
        self.generate_maze_with_guaranteed_path()
        self.calculate_optimal_path()
        self.update_ui()
        
    def generate_maze_with_guaranteed_path(self):
        """Generate maze ensuring valid solution path with mandatory tolls"""
        max_attempts = 10
        for attempt in range(max_attempts):
            self.walls = set()
            self.tolls = {}
            
            solution_path = self.create_solution_path_with_tolls()
            self.add_safe_walls(solution_path)
            self.add_random_tolls(solution_path)
            
            if self.verify_maze_requirements():
                self.game_count += 1
                if self.game_count >= GAMES_NEEDED_FOR_HINTS:
                    self.show_hints = True
                    messagebox.showinfo("Hint System Unlocked", 
                                      "Smart hints are now available!\n"
                                      "Press 'H' for next move suggestion\n"
                                      "or click 'Optimal Path' for full route")
                return
                
        messagebox.showerror("Generation Error", "Failed to create valid maze after 10 attempts!")
        self.root.quit()
    
    def create_solution_path_with_tolls(self):
        """Create solution path with mandatory tolls"""
        path = [self.player_pos]
        current = self.player_pos
        
        # Place mandatory tolls
        mandatory_tolls = []
        if MIN_TOLLS_TO_CROSS > 0:
            toll1_pos = (
                min(GRID_SIZE-2, max(1, random.randint(GRID_SIZE//3, GRID_SIZE*2//3))),
                min(GRID_SIZE-2, max(1, random.randint(1, GRID_SIZE//2)))
            )
            toll2_pos = (
                min(GRID_SIZE-2, max(1, random.randint(GRID_SIZE*2//3, GRID_SIZE-1))),
                min(GRID_SIZE-2, max(1, random.randint(GRID_SIZE//2, GRID_SIZE-1)))
            )
            mandatory_tolls = [toll1_pos, toll2_pos]
        
        for toll_pos in mandatory_tolls:
            while current[0] < toll_pos[0]:
                current = (current[0]+1, current[1])
                path.append(current)
            while current[1] < toll_pos[1]:
                current = (current[0], current[1]+1)
                path.append(current)
            
            self.add_toll(current)
        
        while current[0] < self.destination[0]:
            current = (current[0]+1, current[1])
            path.append(current)
        while current[1] < self.destination[1]:
            current = (current[0], current[1]+1)
            path.append(current)
        
        return path
    
    def add_safe_walls(self, solution_path):
        """Add walls that don't block solution path"""
        solution_cells = set(solution_path)
        wall_count = random.randint(int(GRID_SIZE*GRID_SIZE*0.15), int(GRID_SIZE*GRID_SIZE*0.25))
        
        while len(self.walls) < wall_count:
            r, c = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if (r,c) not in solution_cells and (r,c) not in [self.player_pos, self.destination]:
                self.walls.add((r,c))
    
    def add_random_tolls(self, solution_path):
        """Add additional random tolls"""
        solution_cells = set(solution_path)
        toll_count = random.randint(5, 8)
        
        while len(self.tolls) < toll_count:
            r, c = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if (r,c) not in self.walls and (r,c) not in [self.player_pos, self.destination]:
                self.add_toll((r,c))
    
    def add_toll(self, pos):
        """Add toll plaza at position"""
        toll = random.choice(TOLL_EMOJIS)
        weather, weather_data = random.choice(list(WEATHERS.items()))
        base_cost = random.randint(5, 15) * self.level
        final_cost = int(base_cost * weather_data["multiplier"])
        self.tolls[pos] = {
            "emoji": toll,
            "cost": final_cost,
            "weather": weather,
            "message": weather_data["message"]
        }
    
    def verify_maze_requirements(self):
        """Verify maze meets all requirements"""
        start = self.player_pos
        end = self.destination
        visited = set()
        queue = deque([(start, 0, [])])
        
        while queue:
            pos, tolls_crossed, path = queue.popleft()
            
            if pos == end:
                if tolls_crossed >= MIN_TOLLS_TO_CROSS:
                    return True
                else:
                    continue
                    
            if pos in visited:
                continue
                
            visited.add(pos)
            
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = pos[0]+dr, pos[1]+dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    if (nr,nc) not in self.walls:
                        new_tolls = tolls_crossed
                        if (nr,nc) in self.tolls:
                            new_tolls += 1
                        queue.append(((nr,nc), new_tolls, path + [(nr,nc)]))
        
        return False

    def calculate_optimal_path(self):
        """Calculate optimal path considering toll costs"""
        start = self.player_pos
        end = self.destination
        heap = [(0, 0, 0, [start])]
        visited = {}
        
        while heap:
            total_cost, steps, tolls_crossed, path = heapq.heappop(heap)
            current = path[-1]
            
            if current == end and tolls_crossed >= MIN_TOLLS_TO_CROSS:
                self.optimal_path = path
                return
                
            if current in visited and visited[current] <= tolls_crossed:
                continue
                
            visited[current] = tolls_crossed
            
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = current[0]+dr, current[1]+dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    if (nr,nc) not in self.walls:
                        new_path = path.copy()
                        new_path.append((nr,nc))
                        
                        additional_cost = 0
                        new_tolls = tolls_crossed
                        if (nr,nc) in self.tolls:
                            additional_cost = self.tolls[(nr,nc)]["cost"]
                            new_tolls += 1
                        
                        heapq.heappush(
                            heap, 
                            (total_cost + additional_cost + 1, steps + 1, new_tolls, new_path)
                        )
        
        self.optimal_path = self.find_any_valid_path()

    def find_any_valid_path(self):
        """Find any valid path (safety net)"""
        start = self.player_pos
        end = self.destination
        visited = set()
        queue = deque([(start, [])])
        
        while queue:
            pos, path = queue.popleft()
            
            if pos == end:
                return path
                
            if pos in visited:
                continue
                
            visited.add(pos)
            
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = pos[0]+dr, pos[1]+dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    if (nr,nc) not in self.walls:
                        queue.append(((nr,nc), path + [(nr,nc)]))
        
        return []

    def show_next_hint(self):
        """Show next optimal move as hint"""
        if not self.show_hints or not self.optimal_path:
            messagebox.showinfo("No Hints", "Hints will be available after playing a few games!")
            return
            
        if self.current_hint_index >= len(self.optimal_path) - 1:
            messagebox.showinfo("No More Hints", "You're already at the destination!")
            return
            
        next_move = self.optimal_path[self.current_hint_index + 1]
        current = self.optimal_path[self.current_hint_index]
        
        direction = ""
        if next_move[0] < current[0]:
            direction = "UP ↑"
        elif next_move[0] > current[0]:
            direction = "DOWN ↓"
        elif next_move[1] < current[1]:
            direction = "LEFT ←"
        elif next_move[1] > current[1]:
            direction = "RIGHT →"
        
        messagebox.showinfo(
            "Next Move Hint", 
            f"Optimal next move: {direction}\n"
            f"Position: {next_move}\n"
            f"Press arrow keys to move {direction.split()[0]}"
        )
        self.current_hint_index += 1
        self.highlight_cell(next_move)

    def show_full_optimal_path(self):
        """Show complete optimal path"""
        if not self.show_hints:
            messagebox.showinfo("No Hints", "Complete the tutorial games to unlock this feature!")
            return
            
        if not self.optimal_path:
            messagebox.showinfo("No Path", "No optimal path found!")
            return
            
        path_str = " → ".join([f"({r},{c})" for r, c in self.optimal_path])
        messagebox.showinfo(
            "Optimal Path", 
            f"Cheapest path to destination:\n{path_str}\n"
            f"Estimated total cost: ₹{self.calculate_path_cost(self.optimal_path)}"
        )
        
        self.update_ui()
        for r, c in self.optimal_path[1:-1]:
            self.highlight_cell((r, c), temporary=False)

    def calculate_path_cost(self, path):
        """Calculate total cost of a path"""
        cost = 0
        for r, c in path:
            if (r, c) in self.tolls:
                cost += self.tolls[(r, c)]["cost"]
        return cost

    def highlight_cell(self, pos, temporary=True):
        """Highlight a cell on the grid"""
        r, c = pos
        x1 = c * CELL_SIZE + 2
        y1 = r * CELL_SIZE + 2
        x2 = x1 + CELL_SIZE - 4
        y2 = y1 + CELL_SIZE - 4
        
        highlight = self.canvas.create_oval(
            x1, y1, x2, y2,
            outline="green", width=3, dash=(5, 3)
        )
        
        if temporary:
            self.canvas.after(2000, lambda: self.canvas.delete(highlight))
            self.canvas.create_text(
                x1 + CELL_SIZE//2 - 10,
                y1 + CELL_SIZE//2 - 10,
                text=HINT_EMOJI,
                font=("Arial", 12),
                tags="hint"
            )
            self.canvas.after(2000, lambda: self.canvas.delete("hint"))

    def move(self, dr, dc):
        """Handle player movement"""
        r, c = self.player_pos
        nr, nc = r + dr, c + dc
        
        if not (0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE):
            messagebox.showwarning("Invalid Move", "You can't move outside the grid!")
            return
            
        if (nr, nc) in self.walls:
            messagebox.showwarning("Wall Hit!", f"You crashed into a wall {WALL_EMOJI}")
            return
            
        self.player_pos = (nr, nc)
        self.path.append((nr, nc))
        
        if self.show_hints and self.optimal_path:
            if self.current_hint_index < len(self.optimal_path) - 1:
                if (nr, nc) == self.optimal_path[self.current_hint_index + 1]:
                    self.current_hint_index += 1
                else:
                    self.calculate_optimal_path()
                    self.current_hint_index = 0
        
        if (nr, nc) in self.tolls:
            toll = self.tolls[(nr, nc)]
            if self.money < toll["cost"]:
                messagebox.showerror("Game Over", f"Ran out of money at {toll['emoji']} toll!\nNeeded ₹{toll['cost']} but only had ₹{self.money}")
                self.root.quit()
                return
                
            self.money -= toll["cost"]
            self.total_cost += toll["cost"]
            messagebox.showinfo(
                "Toll Paid", 
                f"{toll['emoji']} Toll: ₹{toll['cost']}\n"
                f"{toll['message']}\n"
                f"Remaining money: ₹{self.money}"
            )
            del self.tolls[(nr, nc)]
        
        if self.player_pos == self.destination:
            level_bonus = 100 * self.level
            self.money += level_bonus
            messagebox.showinfo(
                "Level Complete!", 
                f"🎉 Reached destination!\n"
                f"Level Bonus: ₹{level_bonus}\n"
                f"Total spent: ₹{self.total_cost}\n"
                f"New balance: ₹{self.money}"
            )
            
            if self.level < MAX_LEVELS:
                self.level += 1
                self.start_level()
            else:
                messagebox.showinfo(
                    "You Win!", 
                    f"Completed all {MAX_LEVELS} levels!\n"
                    f"Final Score: ₹{self.money}\n"
                    f"Total Tolls Paid: {self.total_cost}"
                )
                self.root.quit()
        
        self.update_ui()
    
    def update_ui(self):
        """Update all visual elements"""
        self.canvas.delete("all")
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.draw_cell(r, c)
        
        for i in range(len(self.path)-1):
            x1, y1 = self.path[i][1] * CELL_SIZE + CELL_SIZE//2, self.path[i][0] * CELL_SIZE + CELL_SIZE//2
            x2, y2 = self.path[i+1][1] * CELL_SIZE + CELL_SIZE//2, self.path[i+1][0] * CELL_SIZE + CELL_SIZE//2
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=3)
        
        self.level_label.config(text=f"Level: {self.level}/{MAX_LEVELS}")
        self.money_label.config(text=f"Money: ₹{self.money} | Tolls Paid: ₹{self.total_cost}")
        
        if self.player_pos in self.tolls:
            toll = self.tolls[self.player_pos]
            self.weather_label.config(text=f"Weather: {toll['weather']} (Cost ×{WEATHERS[toll['weather']]['multiplier']:.1f})")
        else:
            self.weather_label.config(text="Weather: Normal")
    
    def draw_cell(self, r, c):
        """Draw a single cell on the grid"""
        x1 = c * CELL_SIZE
        y1 = r * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        
        if (r, c) in self.walls:
            color = "#333333"
        elif (r, c) == self.destination:
            color = "#FFD700"
        elif (r, c) in self.tolls:
            color = "#FFA07A"
        else:
            color = "#E6E6FA"
        
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#888")
        
        text = ""
        if (r, c) in self.walls:
            text = WALL_EMOJI
        elif (r, c) in self.tolls:
            text = self.tolls[(r, c)]["emoji"]
        elif (r, c) == self.player_pos:
            text = CAR_EMOJI
        elif (r, c) == self.destination:
            text = DESTINATION_EMOJI
            
        if text:
            self.canvas.create_text(
                x1 + CELL_SIZE//2,
                y1 + CELL_SIZE//2,
                text=text,
                font=("Arial", 24)
            )
            
        if (r, c) in self.tolls:
            self.canvas.create_text(
                x1 + CELL_SIZE//2,
                y1 + CELL_SIZE//4,
                text=f"₹{self.tolls[(r, c)]['cost']}",
                font=("Arial", 10, "bold")
            )

if __name__ == "__main__":
    root = tk.Tk()
    game = TollTrekMaze(root)
    root.mainloop()
