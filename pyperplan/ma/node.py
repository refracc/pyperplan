class StateManager:
    def __init__(self):
        self.states = {}

    def add_state(self, state):
        state_key = frozenset(state)
        if state_key not in self.states:
            self.states[state_key] = state
        return self.states[state_key]

    def get_state(self, state):
        state_key = frozenset(state)
        return self.states.get(state_key, None)

    def __repr__(self):
        return f"StateManager({self.states})"


class SearchNode:
    state_manager = StateManager()  # Class-level state manager

    def __init__(self, projected_state, parent, action, h, g, agent, private_parts):
        self.projected_state = self.state_manager.add_state(projected_state)  # Use state manager to store state
        self.parent = parent
        self.action = action
        self.h = h
        self.g = g
        self.agent = agent
        self.private_parts = private_parts

    def apply_action(self, action, new_proj_state, new_priv_parts):
        new_state = self.state_manager.add_state(new_proj_state)  # Use state manager for new state
        return SearchNode(
            new_state,
            self,
            action,
            self.h,
            self.g + 1,
            self.agent,
            new_priv_parts
        )

    def __hash__(self):
        return hash((frozenset(self.projected_state), self.action, self.h, self.g, self.agent,
                     frozenset(self.private_parts)))

    def __eq__(self, other):
        if not isinstance(other, SearchNode):
            return False
        return (self.projected_state == other.projected_state and
                self.action == other.action and
                self.h == other.h and
                self.g == other.g and
                self.agent == other.agent and
                self.private_parts == other.private_parts)

    def get_public_projection(self, state):
        return state & self.agent.public_predicates

    def __repr__(self):
        return f"SearchNode({self.projected_state}, {self.action}, {self.h}, {self.g}, {self.agent})"
