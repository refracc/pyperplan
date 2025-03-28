#
# This file is part of pyperplan.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

"""
This module contains all data structures needed to represent a PDDL domain and
possibly a task definition.
"""
import time
from heapq import heappop, heappush
from queue import Queue

from pyperplan.ma.node import SearchNode


class Type:
    """
    This class represents a PDDL type.
    """

    def __init__(self, name, parent=None):
        self.name = name.lower()
        self.parent = parent

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Predicate:
    def __init__(self, name, signature, private=False):
        """
        name: The name of the predicate.
        signature: A list of tuples (name, [types]) to represent a list of
                   parameters and their type(s).
        """
        self.name = name
        self.signature = signature
        self.private = private

    def __repr__(self):
        return self.name + str(self.signature)

    def __str__(self):
        return self.name + str(self.signature)

    def __eq__(self, other):
        return isinstance(other, Predicate) and self.name == other.name and self.signature == other.signature

    def __hash__(self):
        return hash(self.name)


# Formula is unused right now!
# class Formula:
#    def __init__(self, operator, operands=[]):
#        # right now we only need AND
#        self._operator = operator # 'AND' | 'OR' | 'NOT'
#        self._operands = operands
#
#    def getOperator(self):
#        return self._operator
#    operator = property(getOperator)
#
#    def getOperands(self):
#        return self._operands
#    operands = property(getOperands)


class Effect:
    def __init__(self, addlist=None, dellist=None):
        """
        addlist: Set of predicates that have to be true after the action
        dellist: Set of predicates that have to be false after the action
        """
        self.addlist = addlist if addlist is not None else set()
        self.dellist = dellist if dellist is not None else set()


class Action:
    def __init__(self, name, signature, precondition, effect):
        self.name = name
        self.signature = signature
        self.precondition = precondition
        self.effect = effect

    def is_applicable(self, state):
        return self.precondition.issubset(state)

    def apply(self, state):
        new_state = set(state)
        new_state.update(self.effect.addlist)
        new_state.difference_update(self.effect.dellist)
        return frozenset(new_state)

    def project(self, domain, agent):
        projected_preconditions = self.precondition.intersection(domain.predicates)
        projected_add_effects = self.effect.addlist.intersection(domain.predicates)
        projected_remove_effects = self.effect.dellist.intersection(domain.predicates)

        # Debug information
        print(f"Preconditions: {self.precondition}")
        print(f"Domain Predicates: {domain.predicates}")
        print(f"Projected Preconditions: {projected_preconditions}")
        print(f"Projected Add Effects: {projected_add_effects}")
        print(f"Projected Remove Effects: {projected_remove_effects}")

        return projected_preconditions, projected_add_effects, projected_remove_effects, self.name, agent

    def __repr__(self):
        return self.name


class Domain:
    def __init__(self, name, types, predicates, actions, constants=None):
        """
        name: The name of the domain
        types: A dict of typename->Type instances in the domain
        predicates: A list of predicates in the domain
        actions: A list of actions in the domain
        constants: A dict of name->type pairs of the constants in the domain
        """
        self.name = name
        self.types = types
        self.predicates = predicates
        self.actions = actions
        self.constants = constants if constants is not None else set()

    def __repr__(self):
        return (
                "< Domain definition: %s Predicates: %s Actions: %s "
                "Constants: %s >"
                % (
                    self.name,
                    [str(p) for p in self.predicates],
                    [str(a) for a in self.actions],
                    [str(c) for c in self.constants],
                )
        )

    __str__ = __repr__


class Problem:
    def __init__(self, name, domain, objects, init, goal, agents=None):
        """
        name: The name of the problem
        domain: The domain in which the problem has to be solved
        objects: A dict name->type of objects that are used in the problem
        init: A list of predicates describing the initial state
        goal: A list of predicates describing the goal state
        """
        self.name = name
        self.domain = domain
        self.objects = objects
        self.initial_state = init
        self.goal = goal
        self.agents = agents if agents is not None else set()

    def __repr__(self):
        return (
                "< Problem definition: %s "
                "Domain: %s Objects: %s Initial State: %s Goal State : %s >"
                % (
                    self.name,
                    self.domain.name,
                    sorted(self.objects),
                    [str(p) for p in self.initial_state],
                    [str(p) for p in self.goal],
                )
        )

    __str__ = __repr__


def send_message(message_type, content, recipient):
    """
    Send a message to another agent.

    :param message_type: The type of the message to send.
    :param content: The content of the message.
    :param recipient: The agent to receive the message.
    """
    message = {'type': message_type, 'content': content}
    recipient.message_queue.put(message)


class Agent:
    def __init__(self, id, initial_node, public_predicates, domain, main_goal_state):
        self.problem = None
        self.id = id
        self.initial_node = initial_node
        self.public_predicates = public_predicates
        self.message_queue = Queue()
        self.distributed_open_list = set()
        self.local_open_list = set()
        self.closed_list = set()
        self.search_active = True
        self.plans = {}
        self.busy = False
        self.domain = domain
        self.main_goal_state = main_goal_state  # The main goal
        self.nodes_expanded = 0
        self.start_time = None
        self.end_time = None
        self.heuristic_calls = 0
        self.applicable_actions_count = 0
        self.nodes_generated = 0
        self.plan_length = None

    def applicable_actions(self, state):
        applicable = set()
        for action in self.domain.actions:
            if action.precondition.issubset(state):
                applicable.add(action)
        return applicable

    def expand(self, node, distributed=False):
        """
        Expand the current node by generating possible successor states,
        considering sub-goals.
        """
        applicable = self.applicable_actions(node.projected_state)
        new_nodes = set()

        for action in applicable:
            # Ensure new_proj_state is correctly applied as a set or complex object
            new_proj_state = action.apply(node.projected_state)
            new_priv_parts = node.private_parts
            new_node = node.apply_action(action, new_proj_state, new_priv_parts)
            new_nodes.add(new_node)

        # Update local open list for future expansion
        self.local_open_list.update(new_nodes)

        if distributed:
            self.distributed_open_list.update(new_nodes)

    def local_heuristic(self, state):
        """
        Computes the FF heuristic for the given state in the agent's i-projected problem.
        :param state: The current state (set of predicates).
        :return: The heuristic value (integer).
        """
        self.heuristic_calls += 1

        # Check that the state is of type frozenset (expected structure)
        if not isinstance(state, frozenset):
            print(f"Error: Expected frozenset, but got {type(state)}. State: {state}")

        relaxed_plan = self._compute_relaxed_plan(state)
        heuristic_value = len(relaxed_plan)

        return heuristic_value

    def _compute_relaxed_plan(self, state):
        open_list = [(0, frozenset(state))]  # Convert state to frozenset
        closed_list = set()
        action_plan = []

        while open_list:
            cost, current_state = heappop(open_list)

            if self._goal_reached(current_state):
                return action_plan

            if current_state in closed_list:
                continue

            closed_list.add(current_state)

            applicable = [action for action in self.domain.actions if action.is_applicable(current_state)]
            for action in applicable:
                new_state = action.apply(current_state)
                new_state_frozenset = frozenset(new_state)  # Convert new_state to frozenset
                heappush(open_list, (cost + 1, new_state_frozenset))
                action_plan.append(action)

        return action_plan

    def _goal_reached(self, state):
        """
        Checks if all sub-goals are reached and, if so, the main goal.
        :param state: The current state (set of predicates).
        :return: True if all sub-goals are reached and the main goal is achieved.
        """
        return self.main_goal_state.issubset(state)

    # def send_sub_goal_update(self, sub_goal):
    #     """
    #     Send a message to all other agents that a sub-goal has been achieved.
    #     """
    #     for agent in self.problem.agents:
    #         if agent.id != self.id:
    #             message = {
    #                 'type': 'sub_goal_achieved',
    #                 'sub_goal': sub_goal,
    #                 'agent_id': self.id
    #             }
    #             send_message('sub_goal_update', message, agent)
    #
    # def handle_sub_goal_message(self, message):
    #     """
    #     Handle a message indicating that another agent has achieved a sub-goal.
    #     """
    #     sub_goal = message['sub_goal']
    #     sender_id = message['agent_id']
    #
    #     # Update local knowledge
    #     if sub_goal in self.sub_goals:
    #         self.sub_goals.remove(sub_goal)
    #         print(f"Agent {self.id} received sub-goal achievement from Agent {sender_id}: {sub_goal}")
    #
    #     # Check if the agent can now proceed to the main goal if all sub-goals are achieved
    #     if not self.sub_goals:
    #         print(f"Agent {self.id} has achieved all sub-goals and can now focus on the main goal.")

    def dist_heuristic(self, agent, projected_state=None, tuple_=None):
        # TODO: Write heuristic.
        pass

    def reconstruct(self, u, t, sender):
        """
        Reconstruct the plan by tracing back through the search nodes.
        """
        if sender not in self.plans:
            self.plans[sender] = {}

        # Store action name instead of object
        self.plans[sender][t] = u.action.name if u.action else None

        if t == 0:
            return self.plans[sender]
        elif u.action is None:
            return None
        else:
            return self.reconstruct(u.parent, t - 1, sender)

    def start_search(self, problem):
        """
        Start the search process.
        """
        self.start_time = time.time()  # Record the start time
        self.problem = problem
        self.a_star_search(problem)
        self.end_time = time.time()  # Record the end time

    def a_star_search(self, problem):
        """
        Perform a synchronous A* search for the agent.
        """
        # Constants for message types
        PLAN_FOUND = "plan_found"
        TERMINATE = "terminate"

        # Helper to initialize g and h
        def initialise_node(node, parent_g=None):
            """Initialise g and h values for a node."""
            if node.g is None:
                node.g = parent_g + problem.cost(parent_g, node) if parent_g is not None else 0
            if node.h is None:
                node.h = self.local_heuristic(node.projected_state)

        # Initialize open and closed lists
        open_list = []
        closed_list = set()
        initial_node = self.initial_node

        # Ensure the initial node is properly initialized
        initialise_node(initial_node)
        heappush(open_list, (initial_node.g + initial_node.h, initial_node))

        while open_list:
            # Process communication first
            self.process_comm(problem)

            # Get the node with the lowest f = g + h
            _, current_node = heappop(open_list)
            current_state = frozenset(current_node.projected_state)

            # Goal reached: reconstruct the plan and notify
            if self._goal_reached(current_state):
                plan = self.reconstruct(current_node, current_node.g, self.id)
                self.send_message(PLAN_FOUND, plan, problem)
                self.plan_length = current_node.g  # Track plan length
                break

            # Skip if the current state is already processed
            if current_state in closed_list:
                continue

            # Mark the current state as closed and expand it
            closed_list.add(current_state)
            self.expand(current_node, distributed=True)

            for successor in self.local_open_list:
                successor_state = frozenset(successor.projected_state)

                # Ensure successor g and h are initialized
                initialise_node(successor, current_node.g)

                # Add successor to the open list if it is not already processed
                if successor_state not in closed_list:
                    heappush(open_list, (successor.g + successor.h, successor))

        # Send termination message when a plan is found
        if self.plans.get(self.id):
            self.send_message(TERMINATE, self.plans[self.id], problem)

    def get_metrics(self):
        """
        Return the metrics for the agent's search process.
        Time taken is converted to milliseconds and rounded to 3 decimal places.
        """
        if self.end_time and self.start_time:
            time_taken_ms = (self.end_time - self.start_time) * 1000  # Convert to milliseconds
            time_taken_ms = round(time_taken_ms, 4)  # Round to 3 decimal places
        else:
            time_taken_ms = None

        return {
            "agent_id": self.id,
            "nodes_expanded": self.nodes_expanded,
            "time_taken_ms": time_taken_ms,
            "heuristic_calls": self.heuristic_calls,
            "applicable_actions_count": self.applicable_actions_count,
            "nodes_generated": self.nodes_generated,
            "plan_length": self.plan_length,
        }

    def send_message(self, message_type, content, problem):
        """
        Send a message to all other agents using the agent list from the problem.
        """
        for agent in problem.agents:
            if agent.id != self.id:
                send_message(message_type, content, agent)

    def process_comm(self, problem):
        """
        Process messages in the agent's message queue.
        """
        while not self.message_queue.empty():
            message = self.message_queue.get()
            if message['type'] == 'state':
                self.handle_state_message(message['content'])
            elif message['type'] == 'plan_found':
                self.search_active = False
                self.plans[self.id] = message['content']
            elif message['type'] == 'reconstruct':
                self.handle_reconstruct_message(message['content'])
            elif message['type'] == 'terminate':
                self.handle_terminate_message(message['content'])
            # elif message['type'] == 'sub_goal_update':
            #     self.handle_sub_goal_message(message['content'])

    def handle_state_message(self, content):
        """
        Handle a state message from another agent.
        """
        public_state = content['state']
        unique_ids = content['uids']
        sender = content['sender']

        u_sent = None
        for node in self.local_open_list:
            if frozenset(node.projected_state) == frozenset(public_state):
                u_sent = node
                break

        if u_sent is None:
            u_sent = SearchNode(
                projected_state=public_state,
                parent=None,
                action=None,
                h=self.local_heuristic(public_state),
                g=0,
                agent=self.id,
                private_parts=unique_ids
            )
        else:
            u_sent.h = content.get('heuristic', self.local_heuristic(u_sent.projected_state))

        if content.get('distributed', False):
            self.distributed_open_list.add(u_sent)
        else:
            self.local_open_list.add(u_sent)

    def handle_reconstruct_message(self, content):
        """
        Handle a reconstruct message to backtrack a plan.
        """
        public_state = content['state']
        t = content['time']
        sender = content['sender']

        u = None
        for node in self.local_open_list:
            if frozenset(node.projected_state) == frozenset(public_state):
                u = node
                break

        if u:
            self.reconstruct(u, t, sender)

    def handle_terminate_message(self, content):
        """
        Handle a termination message indicating the plan is found.
        """
        self.search_active = False
        if content and self.id in self.plans:
            print(f"Agent {self.id} has received a complete plan: {self.plans[self.id]}")
