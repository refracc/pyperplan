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

    def project(self, domain, agent):
        return self.precondition.intersection(domain.predicates), self.effect.addlist.intersection(domain.predicates), self.effect.dellist.intersection(domain.predicates), self.name, agent


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
    message = {'type': message_type, 'content': content, 'recipient': recipient}
    recipient.message_queue.put(message)


class Agent:
    def __init__(self, name, initial_node):
        self.name = name
        self.initial_node = initial_node
        self.public_actions = set()
        self.private_actions = set()
        self.state_mapping = {}
        self.message_queue = []  # Queue for incoming messages
        self.distributed_open_list = set()
        self.local_open_list = set()
        self.closed_list = set()
        self.search_active = True
        self.plans = set()
        self.busy = False

    def heuristic(self, node):
        # Define your heuristic function here
        pass

    def local_heuristic(self, state):
        # Define local heuristic function here
        # TODO: This thing.
        pass

    def distributed_heuristic(self, state):
        # Define distributed heuristic function here
        # TODO: This thing.
        pass

    def process_comm(self, problem):
        """
        Process communication messages received from other agents.
        """
        for m in self.message_queue:
            if m['type'] == 'M_state':
                s_public_projected, delta_tuple = m['content']
                u_sent = self.state_mapping[(s_public_projected, delta_tuple[self.name])]
                s_public_projected = u_sent.projected_state
                u = SearchNode(s_public_projected, m['sender'], None, u_sent.h, u_sent.g, self.name, delta_tuple)

                if m['distributed']:
                    self.distributed_open_list.add(u)
                else:
                    u.h = self.local_heuristic(u.projected_state)  # Local heuristic recomputed
                    self.local_open_list.add(u)

            elif m['type'] == 'M_plan_found':
                self.search_active = False
                self.plans.add((m['sender'], set()))

            elif m['type'] == 'M_reconstruct':
                s_public_projected, delta_i, t, alpha_k = m['content']
                u = self.state_mapping[(s_public_projected, delta_i)]
                self.reconstruct(u, t, alpha_k, problem)

            elif m['type'] == 'M_terminate':
                alpha_k = m['content']  # find out what tf this is...
                received_terminate_from_all = all(
                    alpha_j in self.plans for alpha_j in problem.agents if alpha_j.name is not self.name
                )
                if received_terminate_from_all:
                    minimal_plan = min(self.plans, key=lambda x: len(x[1]))
                    self.report_solution(minimal_plan[1])
                    self.terminate()

            else:
                self.forward_to_distributed_heuristic(m)

    def forward_to_distributed_heuristic(self, message):
        """
        Forward message to distributed heuristic evaluator.
        """
        # Placeholder for actual forwarding logic
        pass

    def reconstruct(self, u, t, alpha_k, problem):
        """
        Reconstruct the plan from the given node.

        :param u: The node from which the plan reconstruction starts.
        :param t: The current time step in the plan.
        :param alpha_k: The agent involved in the reconstruction.
        :param problem: The problem instance.
        """
        plan_entry = next((plan for plan in self.plans if plan[0] == alpha_k), None)
        if plan_entry is None:
            self.plans.add((alpha_k, {}))
            plan_entry = next((plan for plan in self.plans if plan[0] == alpha_k), None)

        plan_dict = plan_entry[1]
        plan_dict[t] = u.action
        for t_prime in range(t + 1, len(plan_dict)):
            if t_prime not in plan_dict:
                plan_dict[t_prime] = None

        t -= 1

        if u == self.initial_node:
            for agent in problem.agents:
                if agent.name != self.name:
                    send_message('M_terminate', alpha_k, agent)
        else:
            if u.action is None:
                send_message('M_reconstruct', (u.projected_state, u.private_parts[self.name], t, alpha_k), u.parent)
            else:
                self.reconstruct(u.parent, t, alpha_k, problem)

    def report_solution(self, plan):
        """
        Report the found solution.

        :param plan: The plan to be reported.
        """
        # Placeholder for report solution logic
        pass

    def terminate(self):
        """
        Terminate the search process.
        """
        # Placeholder for terminate logic
        pass
