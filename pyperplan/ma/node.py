class SearchNode:
    def __init__(self, projected_state, parent, action, h, g, agent, private_parts):
        self.projected_state = projected_state  # Keep this as a set
        self.parent = parent
        self.action = action
        self.h = h
        self.g = g
        self.agent = agent
        self.private_parts = private_parts

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

    def apply_action(self, action, new_proj_state, new_priv_parts):
        return SearchNode(
            new_proj_state,
            self,
            action,
            self.h,
            self.g + 1,
            self.agent,
            new_priv_parts
        )

    def get_public_projection(self, state):
        return state & self.agent.public_predicates

    def __repr__(self):
        return f"SearchNode({self.projected_state}, {self.action}, {self.h}, {self.g}, {self.agent})"
