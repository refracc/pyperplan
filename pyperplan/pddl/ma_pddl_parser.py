import re
from collections import defaultdict
from typing import List, Tuple, Set

from pyperplan.pddl.pddl import *


class PDDLParser:
    def __init__(self):
        self.domain_name = ""
        self.requirements = set()
        self.types = {}
        self.predicates = []
        self.actions = []
        self.constants = {}
        self.private_predicates = defaultdict(set)
        self.agents = []
        self.objects = []
        self.init = set()
        self.goal = set()

    def parse_domain(self, domain_pddl: str):
        domain_lines = domain_pddl.split('\n')
        for line in domain_lines:
            self._parse_domain_line(line.strip())

        # Create Domain instance
        domain = Domain(
            name=self.domain_name,
            types=self.types,
            predicates=self.predicates,
            actions=self.actions,
            constants=self.constants
        )

        return domain

    def parse_problem(self, problem_pddl: str, domain: Domain):
        problem_lines = problem_pddl.split('\n')
        for line in problem_lines:
            self._parse_problem_line(line.strip(), domain)

        # Create agent instances
        agents = [
            Agent(
                id=agent_id,
                initial_node=None,  # Set this appropriately
                public_predicates=self.predicates,
                domain=domain,
                goal_state=self.goal
            ) for agent_id in self.agents
        ]

        return agents

    def _parse_domain_line(self, line: str):
        if line.startswith("(:action"):
            action = self._parse_action(line)
            self.actions.append(action)
        elif line.startswith("(:predicates"):
            self.predicates.extend(self._parse_predicates(line))
        elif line.startswith("(:private"):
            agent, predicates = self._parse_private_predicates(line)
            self.private_predicates[agent].update(predicates)
        else:
            match = re.match(r"\(define \(domain (\w+)\)\)", line)
            if match:
                self.domain_name = match.group(1)

    def _parse_problem_line(self, line: str, domain: Domain):
        if line.startswith("(:objects"):
            self.objects.extend(self._parse_objects(line))
        elif line.startswith("(:private"):
            agent, _ = self._parse_private_objects(line)
            self.agents.append(agent)
        elif line.startswith("(:init"):
            self.init.update(self._parse_init(line))
        elif line.startswith("(:goal"):
            self.goal.update(self._parse_goal(line))

    def _parse_action(self, line: str) -> Action:
        # Parsing action name, parameters, preconditions, and effects
        name = re.search(r"(?<=:action\s)\w+", line).group(0)
        parameters = self._parse_parameters(line)
        preconditions = self._parse_preconditions(line)
        effects = self._parse_effects(line)

        return Action(name, parameters, preconditions, effects)

    def _parse_parameters(self, line: str) -> List[Tuple[str, str]]:
        # Extract parameters for an action
        params = re.findall(r"\?(\w+)\s-\s(\w+)", line)
        return [(param[0], param[1]) for param in params]

    def _parse_preconditions(self, line: str) -> Set[Predicate]:
        preconditions = set()
        precondition_match = re.search(r"(?<=:precondition\s\(and\s)(.*?)(?=\))", line)
        if precondition_match:
            precondition_str = precondition_match.group(1)
            preconditions.update(self._parse_predicate_list(precondition_str))
        return preconditions

    def _parse_effects(self, line: str) -> Effect:
        addlist = set()
        dellist = set()
        effect_match = re.search(r"(?<=:effect\s\(and\s)(.*?)(?=\))", line)
        if effect_match:
            effect_str = effect_match.group(1)
            addlist.update(self._parse_predicate_list(effect_str, add=True))
            dellist.update(self._parse_predicate_list(effect_str, add=False))
        return Effect(addlist, dellist)

    def _parse_predicates(self, line: str) -> List[Predicate]:
        predicates = []
        predicate_matches = re.findall(r"\((\w+)\s([^)]+)\)", line)
        for match in predicate_matches:
            name, args = match
            arg_list = [arg.split(" - ") for arg in args.split()]
            signature = [(arg[0], arg[1:]) for arg in arg_list]
            predicates.append(Predicate(name, signature))
        return predicates

    def _parse_private_predicates(self, line: str) -> Tuple[str, List[Predicate]]:
        agent_match = re.search(r"(?<=\(:private\s)(\w+)", line)
        agent = agent_match.group(1) if agent_match else ""
        predicates = self._parse_predicates(line)
        return agent, predicates

    def _parse_objects(self, line: str) -> List[str]:
        object_matches = re.findall(r"(\w+)\s-\s\w+", line)
        return object_matches

    def _parse_private_objects(self, line: str) -> Tuple[str, List[str]]:
        agent_match = re.search(r"(?<=\(:private\s)(\w+)", line)
        agent = agent_match.group(1) if agent_match else ""
        objects = self._parse_objects(line)
        return agent, objects

    def _parse_init(self, line: str) -> Set[str]:
        init_matches = re.findall(r"\((\w+\s[^)]+)\)", line)
        return set(init_matches)

    def _parse_goal(self, line: str) -> Set[str]:
        goal_matches = re.findall(r"\((\w+\s[^)]+)\)", line)
        return set(goal_matches)

    def _parse_predicate_list(self, predicate_str: str, add=True) -> List[Predicate]:
        predicates = []
        predicate_matches = re.findall(r"\((not\s)?(\w+)(.*?)\)", predicate_str)
        for match in predicate_matches:
            neg, name, args = match
            arg_list = args.split()
            signature = [(arg.split("-")[0], arg.split("-")[1]) for arg in arg_list]
            pred = Predicate(name, signature, private=False)
            if (neg and not add) or (not neg and add):
                predicates.append(pred)
        return predicates

# Example Usage:
domain_pddl = """(define (domain blocks)
    (:requirements :typing :multi-agent :unfactored-privacy)
    (:types agent block - object)
    (:predicates
        (on ?x - block ?y - block)
        (ontable ?x - block)
        (clear ?x - block)
        (:private ?agent - agent
            (holding ?agent - agent ?x - block)
            (handempty ?agent - agent)
        )
    )
    (:action pick-up
        :agent ?a - agent
        :parameters (?x - block)
        :precondition (and
            (clear ?x)
            (ontable ?x)
            (handempty ?a)
        )
        :effect (and
            (not (ontable ?x))
            (not (clear ?x))
            (not (handempty ?a))
            (holding ?a ?x)
        )
    )
    (:action put-down
        :agent ?a - agent
        :parameters (?x - block)
        :precondition 
            (holding ?a ?x)
        :effect (and
            (not (holding ?a ?x))
            (clear ?x)
            (handempty ?a)
            (ontable ?x)
        )
    )
    (:action stack
        :agent ?a - agent
        :parameters (?x - block ?y - block)
        :precondition (and
            (holding ?a ?x)
            (clear ?y)
        )
        :effect (and
            (not (holding ?a ?x))
            (not (clear ?y))
            (clear ?x)
            (handempty ?a)
            (on ?x ?y)
        )
    )
    (:action unstack
        :agent ?a - agent
        :parameters (?x - block ?y - block)
        :precondition (and
            (on ?x ?y)
            (clear ?x)
            (handempty ?a)
        )
        :effect (and
            (holding ?a ?x)
            (clear ?y)
            (not (clear ?x))
            (not (handempty ?a))
            (not (on ?x ?y))
        )
    )
)"""

problem_pddl = """(define (problem BLOCKS-4-0) (:domain blocks)
    (:objects
        a - block
        c - block
        b - block
        e - block
        d - block
        g - block
        f - block
        i - block
        h - block
        (:private a1
            a1 - agent
        )
        (:private a2
            a2 - agent
        )
        (:private a3
            a3 - agent
        )
        (:private a4
            a4 - agent
        )
        (:private a5
            a5 - agent
        )
        (:private a6
            a6 - agent
        )
    )
    (:init 
        (ontable a)
        (ontable b)
        (ontable c)
        (ontable d)
        (ontable e)
        (ontable f)
        (ontable g)
        (ontable h)
        (ontable i)
        (clear a)
        (clear b)
        (clear c)
        (clear d)
        (clear e)
        (clear f)
        (clear g)
        (clear h)
        (clear i)
        (handempty a1)
        (handempty a2)
        (handempty a3)
        (handempty a4)
        (handempty a5)
        (handempty a6)
    )
    (:goal 
        (and
            (on a b)
            (on b c)
        )
    )
)"""

parser = PDDLParser()
domain = parser.parse_domain(domain_pddl)
agents = parser.parse_problem(problem_pddl, domain)

print(parser, domain, agents)

# Now agents is a list of Agent objects with the initial domain and problem setup