class SearchNode:
    def __init__(self, projected_state, parent, action, h, g, agent, private_parts):
        """
        Initialise a search node.

        :param projected_state: The i-projected state (public state for the agent).
        :param parent: The parent of the search node (either another node or an agent identifier).
        :param action: The action used to create this state.
        :param h: The heuristic value of the node.
        :param g: The distance (cost) from the initial state to this state.
        :param agent: The agent that owns this node.
        :param private_parts: The n-tuple of private unique identifiers for each agent.
        """
        self.projected_state = projected_state
        self.parent = parent
        self.action = action
        self.h = h
        self.g = g
        self.agent = agent
        self.private_parts = private_parts

    def apply_action(self, axn, new_proj_state, new_priv_parts):
        """
        Apply an action to this node to create a new search node.

        :param axn: The action to be applied.
        :param new_proj_state: The resulting projected state after the action.
        :param new_priv_parts: The updated private parts after the action.
        :return: A new SearchNode instance.
        """
        return SearchNode(
            new_proj_state,
            self,
            axn,
            self.h,  # The heuristic remains the same initially (deferred evaluation).
            self.g + 1,  # Increment the cost by 1.
            self.agent,
            new_priv_parts
        )

    def to_public_node(self):
        """
        Convert this search node to a public search node.

        :return: A new SearchNode instance representing the public node.
        """
        public_state = self.get_public_projection(self.projected_state)
        return SearchNode(public_state, self.parent, self.action, self.h, self.g, self.agent, self.private_parts)

    def get_public_projection(self, state):
        """
        Get the public projection of the state.

        :param state: The state to be projected.
        :return: The public projection of the state.
        """
        # This method should be implemented to return the public part of the state.
        pass


# Example usage:
number_of_agents = 3  # Define the number of agents
initial_state = ...  # Define the initial state according to the instance
initial_private_parts = [0] * number_of_agents  # Initialise private parts for each agent
agent_id = 1  # Define the agent's unique identifier

# Create the initial search node
initial_node = SearchNode(initial_state, None, None, h=0, g=0, agent=agent_id, private_parts=initial_private_parts)

# Simulate applying an action to create a new node
new_projected_state = ...  # Define the new projected state after applying an action
new_private_parts = ...  # Define the new private parts after applying an action
action = ...  # Define the action to be applied

new_node = initial_node.apply_action(action, new_projected_state, new_private_parts)
