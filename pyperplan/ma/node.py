class SearchNode:
    def __init__(self, projected_state, parent, action, h, g, agent, private_parts):
        self.projected_state = projected_state  # Keep this as a set
        print(type(projected_state))
        self.parent = parent
        self.action = action
        self.h = h
        self.g = g
        self.agent = agent
        self.private_parts = private_parts

    def __hash__(self):
        return hash((frozenset(self.projected_state), self.action, self.h, self.g, self.agent, self.private_parts))

    def __eq__(self, other):
        return (frozenset(self.projected_state), self.action, self.h, self.g, self.agent, self.private_parts) == \
               (frozenset(other.projected_state), other.action, other.h, other.g, other.agent, other.private_parts)

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
