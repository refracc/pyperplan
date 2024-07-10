class SearchNode:
    def __init__(self, projected_state, parent, action, h, g, agent, private_parts):
        self.projected_state = projected_state
        self.parent = parent
        self.action = action
        self.h = h
        self.g = g
        self.agent = agent
        self.private_parts = private_parts

    def apply_action(self, axn, new_proj_state, new_priv_parts):
        return SearchNode(
            new_proj_state,
            self,
            axn,
            self.h,
            self.g + 1,
            self.agent,
            new_priv_parts
        )

    def to_public_node(self):
        return SearchNode(self.get_public_projection(self.projected_state), self.parent, self.action, self.h, self.g, self.agent, self.private_parts)

    def get_public_projection(self, state):
        return {pred for pred in state if pred in self.agent.public_predicates}
