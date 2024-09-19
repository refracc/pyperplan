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
from queue import Queue
from heapq import heappop, heappush

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
    def __init__(self, id, initial_node, public_predicates, domain, goal_state):
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
        self.goal_state = goal_state

    def applicable_actions(self, state):
        applicable = set()
        for action in self.domain.actions:
            if action.precondition.issubset(state):
                applicable.add(action)
        return applicable

    def expand(self, node, distributed):
        """
        Expand the given search node to generate successor nodes.
        :param node: The search node to expand.
        :param distributed: Whether we are using the distributed or local heuristic function.
        :return: None
        """
        applicable = self.applicable_actions(node.projected_state)
        new_nodes = set()

        for action in applicable:
            new_proj_state = action.apply(node.projected_state)
            new_priv_parts = node.private_parts  # Update if necessary for the specific problem
            new_node = node.apply_action(action, new_proj_state, new_priv_parts)
            new_node.g = node.g + 1  # Increment the cost
            new_node.h = self.local_heuristic(
                new_proj_state) if not distributed else self.dist_heuristic(
                new_proj_state)  # Update heuristic if needed
            new_nodes.add(new_node)

        self.local_open_list.update(new_nodes)
        if distributed:
            self.distributed_open_list.update(new_nodes)

    def local_heuristic(self, state):
        """
        Computes the FF heuristic for the given state in the agent's i-projected problem.
        :param state: The current state (set of predicates).
        :return: The heuristic value (integer).
        """
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
        Checks if the given state satisfies the goal condition.
        :param state: The current state (set of predicates).
        :return: True if the goal is reached, False otherwise.
        """
        return self.goal_state.issubset(state)

    def dist_heuristic(self, agent, projected_state=None, tuple_=None):
        # TODO: Write heuristic.
        pass

    def reconstruct(self, u, t, sender):
        """
        Reconstruct the plan by tracing back through the search nodes.
        """
        if sender not in self.plans:
            self.plans[sender] = {}

        self.plans[sender][t] = u.action

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
        self.problem = problem
        self.a_star_search(problem)

    def a_star_search(self, problem):
        """
        Perform a synchronous A* search for the agent.
        """
        open_list = []
        closed_list = set()
        initial_node = self.initial_node

        # Ensure g and h are properly initialized
        initial_node.g = initial_node.g if initial_node.g is not None else 0
        initial_node.h = initial_node.h if initial_node.h is not None else self.local_heuristic(
            initial_node.projected_state)

        heappush(open_list, (initial_node.g + initial_node.h, initial_node))

        while open_list:
            # Process communication first
            self.process_comm(problem)

            _, current_node = heappop(open_list)
            current_state = frozenset(current_node.projected_state)

            if self._goal_reached(current_state):
                # Reconstruct the plan and send the "plan_found" message
                plan = self.reconstruct(current_node, current_node.g, self.id)
                self.send_message("plan_found", plan, problem)
                break

            if current_state in closed_list:
                continue

            closed_list.add(current_state)
            self.expand(current_node, distributed=True)

            for successor in self.local_open_list:
                successor_state = frozenset(successor.projected_state)

                # Ensure g and h are initialized for the successor
                successor.g = successor.g if successor.g is not None else current_node.g + problem.cost(current_node,
                                                                                                        successor)
                successor.h = successor.h if successor.h is not None else self.local_heuristic(
                    successor.projected_state)

                if successor_state not in closed_list:
                    heappush(open_list, (successor.g + successor.h, successor))

        # Final message to terminate if a plan is found
        if self.plans.get(self.id):
            self.send_message("terminate", self.plans[self.id], problem)

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

    def handle_state_message(self, content):
        """
        Handle a state message from another agent.
        """
        public_state = content['state']
        unique_ids = content['uids']
        sender = content['sender']

        print(f"Handling state message from {sender}")
        print(f"Public state: {public_state}")
        print(f"Unique IDs: {unique_ids}")

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
            print(f"Created new SearchNode with heuristic: {u_sent.h}")
        else:
            u_sent.h = content.get('heuristic', self.local_heuristic(u_sent.projected_state))
            print(f"Updated heuristic value: {u_sent.h}")

        if content.get('distributed', False):
            self.distributed_open_list.add(u_sent)
            print(f"Added to distributed_open_list: {u_sent}")
        else:
            self.local_open_list.add(u_sent)
            print(f"Added to local_open_list: {u_sent}")

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
