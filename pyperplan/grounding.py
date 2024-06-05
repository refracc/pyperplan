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

"""
Classes and methods for grounding a schematic PDDL task to a STRIPS planning
task.
"""

import itertools
import logging
import re
from pddl.pddl import MultiAgentAction
from collections import defaultdict

from .task import Operator, Task

# controls mass log output
verbose_logging = False


def ground(problem, remove_statics_from_initial_state=True, remove_irrelevant_operators=True):
    """
    Ground the PDDL task and return an instance of the Task class.

    :param problem: A pddl.Problem instance describing the parsed problem
    :param remove_statics_from_initial_state: Remove static variables from initial state
    :param remove_irrelevant_operators: Remove irrelevant operators
    :return: A task.Task instance with the grounded problem
    """
    domain = problem.domain
    actions = domain.actions.values()
    predicates = domain.predicates.values()

    objects = _collect_objects(problem)
    statics = _get_statics(predicates, actions)
    type_map = _create_type_map(objects)
    initial_state = _get_partial_state(problem.initial_state)
    operators = _ground_actions(actions, type_map, statics, initial_state)
    goals = _get_partial_state(problem.goal)
    facts = _collect_facts(operators) | goals

    if remove_statics_from_initial_state:
        initial_state &= facts

    if remove_irrelevant_operators:
        operators = _relevance_analysis(operators, goals)

    return Task(problem.name, facts, initial_state, goals, operators)


def _collect_objects(problem):
    """Collect objects from problem and domain constants."""
    objects = problem.objects.copy()
    objects.update(problem.domain.constants)
    if verbose_logging:
        logging.debug(f"Objects:\n{objects}")
    return objects


def _get_statics(predicates, actions):
    """Determine all static predicates and return them as a list."""

    def get_effects(action):
        return action.effect.addlist | action.effect.dellist

    effects = set(itertools.chain.from_iterable(get_effects(action) for action in actions))
    return [pred.name for pred in predicates if not any(pred.name == eff.name for eff in effects)]


def _create_type_map(objects):
    """Create a map from each type to its objects."""
    type_map = defaultdict(set)
    for object_name, object_type in objects.items():
        while object_type:
            type_map[object_type].add(object_name)
            object_type = object_type.parent
    return type_map


def _get_partial_state(atoms):
    """Return a set of the string representation of the grounded atoms."""
    return frozenset(_get_fact(atom) for atom in atoms)


def _get_fact(atom):
    """Return the string representation of the grounded atom."""
    args = [name for name, types in atom.signature]
    return _get_grounded_string(atom.name, args)


def _ground_actions(actions, type_map, statics, init):
    """Ground a list of actions and return the resulting list of operators."""
    operators = list(itertools.chain.from_iterable(
        _ground_action(action, type_map, statics, init) for action in actions
    ))
    return operators


def _ground_action(action, type_map, statics, init):
    """Ground the action and return the resulting list of operators."""
    param_to_objects = _map_params_to_objects(action.signature, type_map)
    _filter_invalid_static_preconditions(param_to_objects, action.precondition, statics, init)

    domain_lists = [
        [(name, obj) for obj in objects] for name, objects in param_to_objects.items()
    ]
    assignments = itertools.product(*domain_lists)

    if isinstance(action, MultiAgentAction):
        agents = action.agents
        assignments = ((assign, agent) for assign in assignments for agent in agents if
                       action.can_be_performed_by(agent))
        ops = [
            _create_operator(action, dict(assign), agent, statics, init) for assign, agent in assignments
        ]
    else:
        ops = [
            _create_operator(action, dict(assign), None, statics, init) for assign in assignments
        ]

    return list(filter(None, ops))


def _map_params_to_objects(signature, type_map):
    """Map each parameter to its corresponding objects."""
    param_to_objects = {}
    for param_name, param_types in signature:
        objects = set(itertools.chain.from_iterable(type_map[_type] for _type in param_types))
        param_to_objects[param_name] = objects
    return param_to_objects


def _filter_invalid_static_preconditions(param_to_objects, preconditions, statics, init):
    """Filter out invalid static preconditions from the parameter objects."""
    for param, objects in param_to_objects.items():
        for pred in preconditions:
            if pred.name in statics:
                sig_pos = next((i for i, (var, _) in enumerate(pred.signature) if var == param), -1)
                if sig_pos != -1:
                    objects -= {o for o in objects if not _find_pred_in_init(pred.name, o, sig_pos, init)}


def _find_pred_in_init(pred_name, param, sig_pos, init):
    """Check if an instantiation of the predicate is present in the initial condition."""
    if sig_pos == 0:
        match_init = re.compile(rf"\({pred_name} {param}.*")
    else:
        reg_ex = rf"\({pred_name} " + r"[\w\d-]+\s+" * sig_pos + rf"{param}.*"
        match_init = re.compile(reg_ex)
    return any(match_init.match(string) for string in init)


def _create_operator(action, assignment, agent, statics, init):
    """Create an operator for the given action and assignment."""
    precondition_facts = set()
    for precondition in action.precondition:
        fact = _ground_atom(precondition, assignment)
        if precondition.name in statics and fact not in init:
            return None
        precondition_facts.add(fact)

    add_effects = _ground_atoms(action.effect.addlist, assignment)
    del_effects = _ground_atoms(action.effect.dellist, assignment) - add_effects
    add_effects -= precondition_facts

    args = [assignment[name] for name, types in action.signature]
    name = _get_grounded_string(action.name, args)
    if agent:
        name += f" {agent}"

    return Operator(name, precondition_facts, add_effects, del_effects)


def _ground_atom(atom, assignment):
    """Return a string with the grounded representation of the atom."""
    names = [assignment.get(name, name) for name, _ in atom.signature]
    return _get_grounded_string(atom.name, names)


def _ground_atoms(atoms, assignment):
    """Return a set of the grounded representation of the atoms."""
    return {_ground_atom(atom, assignment) for atom in atoms}


def _get_grounded_string(name, args):
    """Return the lisp notation string for the grounded atom or action."""
    return f"({name}{' ' + ' '.join(args) if args else ''})"


def _collect_facts(operators):
    """Collect all facts from grounded operators."""
    facts = set()
    for op in operators:
        facts |= op.preconditions | op.add_effects | op.del_effects
    return facts


def _relevance_analysis(operators, goals):
    """Perform relevance analysis on operators based on goals."""
    relevant_facts = set(goals)
    old_relevant_facts = set()

    while relevant_facts != old_relevant_facts:
        old_relevant_facts = relevant_facts.copy()
        for op in operators:
            if op.add_effects & relevant_facts or op.del_effects & relevant_facts:
                relevant_facts |= op.preconditions

    del_operators = {op for op in operators if not (op.add_effects & relevant_facts or op.del_effects & relevant_facts)}
    return [op for op in operators if op not in del_operators]
