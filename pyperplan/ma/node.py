from pyperplan.pddl.pddl import Agent


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

    @staticmethod
    def search(agent, initial_node, goal):
        """
        Perform the search algorithm for a given agent starting from an initial node.

        :param agent: The agent performing the search.
        :param initial_node: The initial search node.
        :param goal: The goal state.
        :return: None
        """
        agent.distributed_open_list = {initial_node}
        agent.local_open_list = {initial_node}
        agent.closed_list = set()
        initial_node.g = 0
        initial_node.h = agent.heuristic(initial_node)
        agent.busy = False
        agent.search = True

        while agent.search:
            agent.process_comm()

            if not agent.busy:
                if agent.distributed_open_list:
                    u = min(agent.distributed_open_list, key=lambda node: node.h)
                elif agent.local_open_list:
                    u = min(agent.local_open_list, key=lambda node: node.h)
                else:
                    continue

                SearchNode.process_node(agent, u, goal)

            # Local search loop
            while (not agent.distributed_open_list or agent.busy) and agent.local_open_list:
                u = min(agent.local_open_list, key=lambda node: node.h)
                SearchNode.process_node(agent, u, goal)
                agent.process_comm()

    @staticmethod
    def process_node(agent, u, goal):
        """
        Process a search node.

        :param agent: The agent performing the search.
        :param u: The search node to process.
        :param goal: The goal state.
        :return: None
        """
        if u not in agent.closed_list:
            agent.closed_list.add(u)  # Close the search node
            if goal.issubset(u.projected_state):
                agent.search_active = False  # End search
                agent.send_plan_found_message()
                agent.reconstruct_plan(u, u.g)
            else:
                agent.expand(u, agent.distributed_open_list)

    @staticmethod
    def expand(agent: Agent, u, d):
        """
        Expand a search node.

        :param agent: The agent performing the search.
        :param u: The search node to expand.
        :param d: Boolean indicating whether this is a distributed search.
        :return: None
        """
        if not d:
            u.h = agent.local_heuristic(u.projected_state)
        else:
            u.h = agent.distributed_heuristic(u.projected_state)
            agent.busy = True  # Set busy when distributed heuristic starts evaluation

        if u.action in agent.public_actions:
            public_node = u.to_public_node()
            agent.send_state_message(public_node.projected_state, public_node.private_parts, public_node.h, d)
            agent.mapping[(public_node.projected_state, public_node.private_parts[agent.name])] = public_node

            e = set()
            for action in agent.private_actions:
                if action.preconditions.issubset(u.projected_state):
                    new_proj_state = agent.apply_action_to_state(action, u.projected_state)
                    new_priv_parts = agent.update_private_parts(u.private_parts, action)
                    new_node = u.apply_action(action, new_proj_state, new_priv_parts)
                    new_node.g = u.g + 1
                    e.add(new_node)

            agent.local_open_list.update([node for node in e if node not in agent.closed_list])

            if d:
                agent.distributed_open_list.update([node for node in e if node not in agent.closed_list])
