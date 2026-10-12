TA1/TA1.py
import agentpy as ap
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- 1. Get user input from console (INPUT) ---
print("\n--- RANDOM WALK SIMULATION SETUP ---")
num_agents = int(input("Enter number of agents: "))
grid_size = int(input("Enter grid size (e.g., 10 for 10x10): "))
num_steps = int(input("Enter number of steps: "))

# --- 2. Define the Agent and Model (PROCESS) ---
class RandomWalker(ap.Agent):
    def setup(self):
        # Initialize random starting position
        self.position = (random.randint(0, self.model.p.grid_size[0]-1),
                         random.randint(0, self.model.p.grid_size[1]-1))
        # Create lists to record the path history 
        self.history_x = [self.position[0]]
        self.history_y = [self.position[1]]

    def step(self):
        direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        x, y = self.position
        
        # Keep agents inside grid limits (bounded movement)
        x = max(0, min(self.model.p.grid_size[0]-1, x + direction[0]))
        y = max(0, min(self.model.p.grid_size[1]-1, y + direction[1]))
        
        self.position = (x, y)
        
        # Record the new coordinates to the history
        self.history_x.append(x)
        self.history_y.append(y)

class RandomWalkModel(ap.Model):
    def setup(self):
        self.agents = ap.AgentList(self, self.p.agents, RandomWalker)
        self.grid = ap.Grid(self, self.p.grid_size, torus=False)
        self.grid.add_agents(self.agents)

    def step(self):
        self.agents.step()

    def end(self):
        # Output recorded paths and final positions to the terminal (OUTPUT)
        print("\n--- SIMULATION RESULTS ---")
        print(f"Simulation completed with {self.p.agents} agents over {self.p.steps} steps.\n")
        
        for i, agent in enumerate(self.agents):
            recorded_path = list(zip(agent.history_x, agent.history_y))
            print(f"Agent {i+1}:")
            print(f" - Recorded Path: {recorded_path}")
            print(f" - Final Position: {agent.position}\n")
            
        print("--------------------------\n")

# Assign parameters based on user input
parameters = {
    'agents': num_agents,
    'grid_size': (grid_size, grid_size),
    'steps': num_steps
}

model = RandomWalkModel(parameters)
model.setup()

# --- 3. Execute Simulation FIRST ---
# Run all mathematical steps instantly behind the scenes so terminal prints immediately
for _ in range(model.p.steps):
    model.step()

# Print the final results to the terminal IMMEDIATELY
model.end()

# --- 4. Interactive Animation with Paths (VISUALIZATION) ---
print("Generating live animation in a new window...")

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(0, model.p.grid_size[0])
ax.set_ylim(0, model.p.grid_size[1])
ax.set_xticks(range(model.p.grid_size[0]+1))
ax.set_yticks(range(model.p.grid_size[1]+1))
ax.grid(True)
ax.set_title('Random Walk Simulation - Multi-Agent Trajectories')

# Setup dots (current position) and lines (recorded path history)
scat = ax.scatter([], [], s=200, zorder=3) 
lines = [ax.plot([], [], alpha=0.5, linewidth=2, zorder=2)[0] for _ in range(model.p.agents)]

def update(frame):
    # Read from the pre-recorded history instead of calculating new steps
    x = [agent.history_x[frame] for agent in model.agents]
    y = [agent.history_y[frame] for agent in model.agents]
    scat.set_offsets(list(zip(x, y)))
    
    # Draw lines up to the current frame
    for i, agent in enumerate(model.agents):
        lines[i].set_data(agent.history_x[:frame+1], agent.history_y[:frame+1])
        
    return [scat] + lines

# frames = model.p.steps + 1 because history includes the starting position (frame 0)
ani = animation.FuncAnimation(fig, update, frames=model.p.steps + 1, blit=True, repeat=False)

plt.show()
