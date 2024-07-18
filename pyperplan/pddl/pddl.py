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
from pyperplan.ma.node import SearchNode


class Type:
    """
    This class represents a PDDL type.
    """

    # Class-level attribute to store the "object" type
    _object_type = None

    def __init__(self, name, parent=None):
        self.name = name.lower()

        # Ensure the "object" type is initialized only once
        if Type._object_type is None:
            Type._object_type = self if name.lower() == "object" else Type._object_type == Type("object")

        # Assign the parent type
        if parent is None:
            self.parent = Type._object_type
        else:
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
        """
        name: The name identifying the action
        signature: A list of tuples (name, [types]) to represent a list of
                   parameters and their type(s).
        precondition: A list of predicates that have to be true before the
                      action can be applied
        effect: An effect instance specifying the postcondition of the action
        """
        self.name = name
        self.signature = signature
        self.precondition = precondition
        self.effect = effect

    def is_applicable(self, state):
        return self.precondition.issubset(state)

    def apply(self, state):
        new_state = state.copy()
        new_state.update(self.effect.addlist)
        new_state.difference_update(self.effect.dellist)
        return new_state

    def project(self, domain, agent):
        """
        Project the action to the given domain and agent.

        :param domain: The domain containing predicates.
        :param agent: The agent identifier.
        :return: A tuple of projected preconditions, add effects, delete effects, action name, and agent.
        """
        projected_preconditions = self.precondition.intersection(domain.predicates)
        projected_add_effects = self.effect.addlist.intersection(domain.predicates)
        projected_remove_effects = self.effect.dellist.intersection(domain.predicates)

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
    def __init__(self, id, initial_node, public_predicates):
        self.id = id
        self.initial_node = initial_node
        self.public_predicates = public_predicates
        self.state_mapping = {}
        self.message_queue = []
        self.distributed_open_list = set()
        self.local_open_list = set()
        self.closed_list = set()
        self.search_active = True
        self.plans = {}
        self.busy = False

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
        :param distributed: Whether the expansion is for the distributed open list.
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
                new_proj_state) if not distributed else self.dist_heuristic(new_proj_state)  # Update heuristic if needed
            new_nodes.add(new_node)

        self.local_open_list.update(new_nodes)
        if distributed:
            self.distributed_open_list.update(new_nodes)

    def process_comm(self):
        for message in self.message_queue:
            if message['type'] == 'state':
                public_state = message['state']
                unique_ids = message['uids']
                sender = message['sender']

                u_sent = self.state_mapping.get((public_state, unique_ids[self.id]))
                if u_sent:
                    u = SearchNode(
                        projected_state=u_sent.projected_state,
                        parent=sender,
                        action=None,
                        h=message['heuristic'],
                        g=u_sent.g,
                        agent=self.id,
                        private_parts=unique_ids
                    )
                    if message['distributed']:
                        self.distributed_open_list.add(u)
                    else:
                        u.h = self.local_heuristic(u.projected_state)
                        self.local_open_list.add(u)

            elif message['type'] == 'plan_found':
                self.search_active = False
                self.plans[self.id] = message['plan']

            elif message['type'] == 'reconstruct':
                public_state = message['state']
                uid = message['uid']
                t = message['time']
                sender = message['sender']

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
        # TODO: Write heuristic.
        pass

    def dist_heuristic(self, agent, projected_state, tuple_):
        # TODO: Write heuristic.
        pass

    def reconstruct(self, u, t, sender):
        plan = self.plans.get(sender)
        if plan is None:
            self.plans[sender] = {}
        self.plans[sender][t] = u.action

        if t == 0:
            self.message_queue.append({"terminate", u, sender})  # send terminate message.
        elif u.action is None:
            self.message_queue.append({"reconstruct", u, sender})  # send reconstruct message.
        else:
            self.reconstruct(u.parent, t - 1, sender)
