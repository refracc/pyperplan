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
                   parameters an their type(s).
        precondition: A list of predicates that have to be true before the
                      action can be applied
        effect: An effect instance specifying the postcondition of the action
        """
        self.name = name
        self.signature = signature
        self.precondition = precondition
        self.effect = effect


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


class Agent:

    def __init__(self, name, type):
        """
        :param name: The name of the agent.
        """
        self.name = name
        self.type = type
        self.distributed_open_list = list()
        self.local_open_list = list()
        self.closed_list = list()
        self.busy = False
        self.search = True
        self.distributed_estimator = 0
        self.local_estimator = 0
        self.mapping = dict
        self.plans = set()
        self.public_actions = set()
        self.private_actions = set()


    def heuristic(self, node):
        # Define your heuristic function here
        pass

    def local_heuristic(self, state):
        # Define local heuristic function here
        pass

    def distributed_heuristic(self, state):
        # Define distributed heuristic function here
        pass

    def process_comm(self):
        # Define communication processing logic here
        pass

    def send_plan_found_message(self):
        # Logic to send PLANFOUND message to all agents
        pass

    def reconstruct_plan(self, u, cost):
        # Define your plan reconstruction logic here
        pass

    def apply_action_to_state(self, action, state):
        # Apply the action to the state and return the new state
        pass

    def update_private_parts(self, private_parts, action):
        # Update the private parts based on the action
        pass

    def send_state_message(self, state, private_parts, heuristic, distributed):
        # Send the state message
        pass

