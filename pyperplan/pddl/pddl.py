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
        self.state_mapping = {}
        self.message_queue = Queue()
        self.distributed_open_list = set()
        self.local_open_list = set()
        self.closed_list = set()
        self.search_active = True
        self.plans = {}
        self.busy = False
        self.domain = domain
        self.goal_state = goal_state

    def applicable_actions(self, state, domain):
        """
        Get a set of all applicable actions from the given state.
        :param state: The current state (set of predicates).
        :param domain: An instance of the domain
        :return: A set of applicable actions.
        """
        return {action for action in domain.actions if action.is_applicable(state)}

    def expand(self, node, distributed, domain):
        """
        Expand the given search node to generate successor nodes.
        :param node: The search node to expand.
        :param distributed: Whether we are using the distributed or local heuristic function.
        :param domain: The domain for the problem.
        :return: None
        """
        applicable_actions = self.applicable_actions(node.projected_state, domain)
        new_nodes = set()

        for action in applicable_actions:
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

    def process_comm(self):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            if message['type'] == 'state':
                content = message['content']
                public_state = content['state']
                unique_ids = content['uids']
                sender = content['sender']

                if self.id >= len(unique_ids):
                    continue  # Skip if the index is out of range

                u_sent = self.state_mapping.get((public_state, unique_ids[self.id]))
                if u_sent:
                    u = SearchNode(
                        projected_state=u_sent.projected_state,
                        parent=sender,
                        action=None,
                        h=content['heuristic'],
                        g=u_sent.g,
                        agent=self.id,
                        private_parts=unique_ids
                    )
                    if content['distributed']:
                        self.distributed_open_list.add(u)
                    else:
                        u.h = self.local_heuristic(u.projected_state)
                        self.local_open_list.add(u)

            elif message['type'] == 'plan_found':
                self.search_active = False
                self.plans[self.id] = message['plan']

            elif message['type'] == 'reconstruct':
                content = message['content']
                public_state = content['state']
                uid = content['uid']
                t = content['time']
                sender = content['sender']

                u = self.state_mapping.get((public_state, uid))
                if u:
                    self.reconstruct(u, t, sender)

            elif message['type'] == 'terminate':
                if all(self.plans.values()):
                    plan = min(self.plans.values(), key=len)
                    print(plan)

            else:
                raise LookupError("The message type provided does not exist.")

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

            applicable_actions = [action for action in self.domain.actions if action.is_applicable(current_state)]
            for action in applicable_actions:
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
        plan = self.plans.get(sender)
        if plan is None:
            self.plans[sender] = {}
        self.plans[sender][t] = u.action

        if t == 0:
            self.message_queue.put({"terminate", u, sender})  # send terminate message.
        elif u.action is None:
            self.message_queue.put({"reconstruct", u, sender})  # send reconstruct message.
        else:
            self.reconstruct(u.parent, t - 1, sender)
