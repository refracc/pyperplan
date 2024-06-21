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

"""
Classes and methods for grounding a schematic PDDL task to a STRIPS planning
task.
"""

from collections import defaultdict
import itertools
import logging
import re

from pyperplan.pddl.pddl import Agent
from pyperplan.task import Operator, Task

# controls mass log output
verbose_logging = True


def process_private_information(problem, agent_name, agent_type):
    """
    Process private predicates and actions for the given agent.

    :param problem: A pddl.Problem instance describing the parsed problem
    :param agent_name: The name of the agent
    :param agent_type: The type of the agent
    :return: A dictionary with grounded private predicates and actions
    """
    agent_instance = Agent(agent_name, agent_type)
    private_predicates = {pred.name for pred in problem.domain.predicates if agent_instance.knows_predicate(pred.name)}
    private_actions = [action for action in problem.domain.actions if
                       any(agent_instance.knows_predicate(pred.name) for pred in action.precondition)]

    # Ground private actions
    type_map = _create_type_map(problem.objects)
    init = _get_partial_state(problem.initial_state)
    statics = _get_statics(problem.domain.predicates, problem.domain.actions)

    grounded_private_actions = _ground_actions(private_actions, type_map, statics, init)

    return {
        "private_predicates": private_predicates,
        "private_actions": grounded_private_actions
    }


def ground(problem, remove_statics_from_initial_state=True, remove_irrelevant_operators=True):
    """
    Ground the PDDL task and return an instance of the task.Task class.

    :param problem: A pddl.Problem instance describing the parsed problem
    :param remove_statics_from_initial_state: Flag to remove static predicates from the initial state
    :param remove_irrelevant_operators: Flag to remove irrelevant operators
    :return: A task.Task instance with the grounded problem
    """
    domain = problem.domain
    actions = domain.actions.values() if isinstance(domain.actions, dict) else domain.actions
    predicates = domain.predicates.values() if isinstance(domain.predicates, dict) else domain.predicates

    # Objects
    objects = problem.objects
    objects.update(domain.constants)
    if verbose_logging:
        print("Objects:\n%s" % objects)

    # Get the names of the static predicates
    statics = _get_statics(predicates, actions)
    if verbose_logging:
        print("Static predicates:\n%s" % statics)

    # Create a map from types to objects
    type_map = _create_type_map(objects)
    if verbose_logging:
        print("Type to object map:\n%s" % type_map)

    # Transform initial state into a specific
    init = _get_partial_state(problem.initial_state)
    if verbose_logging:
        print("Initial state with statics:\n%s" % init)

    # Ground actions
    operators = _ground_actions(actions, type_map, statics, init)
    if verbose_logging:
        print("Operators:\n%s" % "\n".join(map(str, operators)))

    # TODO: Process private information for each agent if agents are provided
    private_info_all_agents = {}
    if problem.agents:
        for agent_name, agent_type in problem.agents.items():
            private_info = process_private_information(problem, agent_name, agent_type)
            private_info_all_agents[agent_name] = private_info
            if verbose_logging:
                print(f"Private information for agent {agent_name}:\n{private_info}")

    # Ground goal
    goals = _get_partial_state(problem.goal)
    if verbose_logging:
        print("Goal:\n%s" % goals)

    # Collect facts from operators and include the ones from the goal
    facts = _collect_facts(operators) | goals
    if verbose_logging:
        print("All grounded facts:\n%s" % facts)

    # Remove statics from initial state
    if remove_statics_from_initial_state:
        init &= facts
        if verbose_logging:
            print("Initial state without statics:\n%s" % init)

    # Perform relevance analysis
    if remove_irrelevant_operators:
        operators = _relevance_analysis(operators, goals)

    name = problem.name
    return Task(name, facts, init, goals, operators, problem.agents)


def _relevance_analysis(operators, goals):
    """This implements a relevance analysis of operators.

    We start with all facts within the goal and iteratively compute
    a fixpoint of all relevant effects.
    Relevant effects are those that contribute to a valid path to the goal.
    """
    debug = True
    debug_pruned_op = set()

    relevant_facts = set()
    old_relevant_facts = set()
    changed = True
    for goal in goals:
        relevant_facts.add(goal)

    while changed:
        # set next relevant facts to current facts
        # if we do not add anything in the following for loop
        # we have already found a fixpoint
        old_relevant_facts = relevant_facts.copy()
        # compute cut of relevant facts with effects of all operators
        for op in operators:
            new_addlist = op.add_effects & relevant_facts
            new_dellist = op.del_effects & relevant_facts
            if new_addlist or new_dellist:
                # add all preconditions to relevant facts
                relevant_facts |= op.preconditions
        changed = old_relevant_facts != relevant_facts

    # delete all irrelevant effects
    del_operators = set()
    for op in operators:
        # calculate new effects
        new_addlist = op.add_effects & relevant_facts
        new_dellist = op.del_effects & relevant_facts
        if debug:
            debug_pruned_op |= op.add_effects - relevant_facts
            debug_pruned_op |= op.del_effects - relevant_facts
        # store new effects
        op.add_effects = new_addlist
        op.del_effects = new_dellist
        if not new_addlist and not new_dellist:
            if verbose_logging:
                print("Relevance analysis removed oparator %s" % op.name)
            del_operators.add(op)
    if debug:
        print("Relevance analysis removed %d facts" % len(debug_pruned_op))
    # remove completely irrelevant operators
    return [op for op in operators if not op in del_operators]


def _get_statics(predicates, actions):
    """
    Determine all static predicates and return them as a list.

    We want to know the statics to avoid grounded actions with static
    preconditions violated. A static predicate is a predicate which
    doesn't occur in an effect of an action.
    """

    def get_effects(action):
        return action.effect.addlist | action.effect.dellist

    effects = [get_effects(action) for action in actions]
    effects = set(itertools.chain(*effects))

    def static(predicate):
        return not any(predicate.name == eff.name for eff in effects)

    statics = [pred.name for pred in predicates if static(pred)]
    return statics


def _create_type_map(objects):
    """
    Create a map from each type to its objects.

    For each object we know the type. This returns a dictionary
    from each type to a set of objects (of this type). We also
    have to care about type hierarchy. An object
    of a subtype is a specialization of a specific type. We have
    to put this object into the set of the supertype, too.
    """
    type_map = defaultdict(set)

    # for every type we append the corresponding object
    for object_name, object_type in objects.items():
        parent_type = object_type.parent
        while True:
            type_map[object_type].add(object_name)
            object_type, parent_type = parent_type, object_type.parent
            if parent_type is None:
                # if object_type is None:
                break

    # TODO sets in map should be ordered lists
    return type_map


def _collect_facts(operators):
    """
    Collect all facts from grounded operators (precondition, add
    effects and delete effects).
    """
    facts = set()
    for op in operators:
        facts |= op.preconditions | op.add_effects | op.del_effects
    return facts


def _ground_actions(actions, type_map, statics, init):
    op_lists = [_ground_action(action, type_map, statics, init) for action in actions]
    operators = list(itertools.chain(*op_lists))
    return operators


def _ground_action(action, type_map, statics, init):
    print("Grounding %s" % action.name)
    param_to_objects = {}

    for param_name, param_types in action.signature:
        objects = [type_map[type] for type in param_types]
        objects = set(itertools.chain(*objects))
        param_to_objects[param_name] = objects

    remove_debug = 0
    for param, objects in param_to_objects.items():
        for pred in action.precondition:
            if pred.name in statics:
                sig_pos = -1
                count = 0
                for var, _ in pred.signature:
                    if var == param:
                        sig_pos = count
                    count += 1
                if sig_pos != -1:
                    obj_copy = objects.copy()
                    for o in obj_copy:
                        if not _find_pred_in_init(pred.name, o, sig_pos, init):
                            if verbose_logging:
                                remove_debug += 1
                            objects.remove(o)
    if verbose_logging:
        print(
            "Static precondition analysis removed %d possible objects" % remove_debug
        )

    domain_lists = [
        [(name, obj) for obj in objects] for name, objects in param_to_objects.items()
    ]
    assignments = itertools.product(*domain_lists)

    ops = [
        _create_operator(action, dict(assign), statics, init) for assign in assignments
    ]
    ops = filter(bool, ops)

    return ops


def _find_pred_in_init(pred_name, param, sig_pos, init):
    """
    This method is used to check whether an instantiation of the predicate
    denoted by pred_name with the parameter param at position sig_pos is
    present in the initial condition.

    Useful to evaluate static preconditions efficiently.
    """
    match_init = None
    if sig_pos == 0:
        match_init = re.compile(rf"\({pred_name} {param}.*")
    else:
        reg_ex = r"\(%s\s+" % pred_name
        reg_ex += r"[\w\d-]+\s+" * sig_pos
        #        for i in xrange(sig_pos):
        #            reg_ex += '[\w\d-]+\s+'
        reg_ex += "%s.*" % param
        match_init = re.compile(reg_ex)
    assert match_init is not None
    return any([match_init.match(string) for string in init])


def _create_operator(action, assignment, statics, init):
    """Create an operator for "action" and "assignment".

    Statics are handled here. True statics aren't added to the
    precondition facts of a grounded operator. If there is a false static
    in the ungrounded precondition, the operator won't be created.
    @param assignment: mapping from predicate name to object name
    """
    precondition_facts = set()
    for precondition in action.precondition:
        fact = _ground_atom(precondition, assignment)
        predicate_name = precondition.name
        if predicate_name in statics:
            # Check if this precondition is false in the initial state
            if fact not in init:
                # This precondition is never true -> Don't add operator
                return None
        else:
            # This precondition is not always true -> Add it
            precondition_facts.add(fact)

    add_effects = _ground_atoms(action.effect.addlist, assignment)
    del_effects = _ground_atoms(action.effect.dellist, assignment)
    # If the same fact is added and deleted by an operator the STRIPS formalism
    # adds it.
    del_effects -= add_effects
    # If a fact is present in the precondition, we do not have to add it.
    # Note that if a fact is in the delete and in the add effects,
    # it has already been deleted in the previous step.
    add_effects -= precondition_facts
    args = [assignment[name] for name, types in action.signature]
    name = _get_grounded_string(action.name, args)
    return Operator(name, precondition_facts, add_effects, del_effects)


def _get_grounded_string(name, args):
    """We use the lisp notation (e.g. "(unstack c e)")."""
    args_string = " " + " ".join(args) if args else ""
    return f"({name}{args_string})"


def _ground_atom(atom, assignment):
    """
    Return a string with the grounded representation of "atom" with respect
    to "assignment".
    """
    names = []
    for name, types in atom.signature:
        if name in assignment:
            names.append(assignment[name])
        else:
            names.append(name)
    return _get_grounded_string(atom.name, names)


def _ground_atoms(atoms, assignment):
    """Return a set of the grounded representation of the atoms."""
    return {_ground_atom(atom, assignment) for atom in atoms}


def _get_fact(atom):
    """Return the string representation of the grounded atom."""
    args = [name for name, types in atom.signature]
    return _get_grounded_string(atom.name, args)


def _get_partial_state(atoms):
    """Return a set of the string representation of the grounded atoms."""
    return frozenset(_get_fact(atom) for atom in atoms)
