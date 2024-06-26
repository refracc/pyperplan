class SearchNode:
    def __init__(self, projected_state, parent, action, h, g, agent, private_parts):
        self.projected_state = projected_state
        self.parent = parent
        self.action = action
        self.h = h
        self.g = g
        self.agent = agent
        self.private_parts = private_parts

