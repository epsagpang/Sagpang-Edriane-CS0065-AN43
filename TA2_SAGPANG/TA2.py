def ask_room_state(room):
    """Ask the user for the initial state of a room until the input is valid."""
    while True:
        answer = input(f"Is room {room} Dirty or Clean? ").strip().lower()
        if answer in ("dirty", "clean"):
            return answer.capitalize()      # stored as 'Dirty' or 'Clean'
        print("  Please type either 'dirty' or 'clean'.")


def is_dirty(environment, room):
    """Return True if the given room is dirty."""
    return environment[room] == "Dirty"


def clean_room(environment, room):
    """Clean the given room (update the environment)."""
    environment[room] = "Clean"


# ----------------------------------------------------------------------
# TASK 2: The rule-based agent
# ----------------------------------------------------------------------
class VacuumAgent:
    def __init__(self, start_room="A"):
        self.location = start_room          # the room the agent is in

    def move(self):
        """Switch to the other room (A <-> B)."""
        self.location = "B" if self.location == "A" else "A"

    def perceive_and_act(self, environment):
        """
        Perceive the current room, then apply the rules.
        Returns a text describing the action taken.
        """
        # Perceive: is the current room dirty?
        if is_dirty(environment, self.location):
            # Rule 1: current room is dirty -> clean it
            clean_room(environment, self.location)
            return f"Room {self.location} has been cleaned."
        else:
            # Rule 2: current room is clean -> move to the other room
            self.move()
            return f"Moving to room {self.location}"


# ----------------------------------------------------------------------
# TASK 3: Run the simulation
# ----------------------------------------------------------------------
def ask_steps():
    """Ask the user how many steps to run (must be a whole number >= 1)."""
    while True:
        try:
            steps = int(input("How many steps should the agent run? "))
            if steps >= 1:
                return steps
        except ValueError:
            pass
        print("  Please enter a whole number of 1 or more.")


def main():
    # Initialize the two rooms using a dictionary
    environment = {"A": None, "B": None}

    # Let the user set the initial state of each room
    for room in environment:
        environment[room] = ask_room_state(room)

    print()
    steps = ask_steps()

    agent = VacuumAgent("A")                # agent starts in room A

    # Run the agent in a loop for the chosen number of steps
    for step in range(1, steps + 1):
        print(f"\nStep {step}: Agent is in room {agent.location}")
        action = agent.perceive_and_act(environment)
        print(action)
        print(f"Environment state: {environment}")


if __name__ == "__main__":
    main()