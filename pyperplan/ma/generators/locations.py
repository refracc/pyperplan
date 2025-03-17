import json
import random
import uuid
from pathlib import Path
from typing import List

from pyperplan.grounding import multi_agent_ground
from pyperplan.pddl.pddl import Problem, Agent, Type, Predicate, Domain, Action, Effect, SearchNode


def _generate_problem_id() -> str:
    return str(uuid.uuid4())


def _solve_problem(problem: Problem):
    """Run the planner for all agents in the problem"""
    for agent in problem.agents:
        agent.start_search(problem)


def _serialize_problem(problem: Problem) -> dict:
    """Convert problem data to JSON-serializable format"""
    num_agents = len(problem.agents)
    num_locations = len(problem.objects)
    translator_facts = (num_agents * num_locations) + (num_locations - 1)

    # Convert Type objects to their names
    objects = {obj: type_.name if isinstance(type_, Type) else str(type_)
               for obj, type_ in problem.objects.items()}

    return {
        "problem_id": problem.name,
        "domain": problem.domain.name,
        "objects": objects,  # Use the converted dictionary
        "initial_state": [str(pred) for pred in problem.initial_state],
        "goal": [str(pred) for pred in problem.goal],
        "agents": [
            {
                "id": agent.id,
                "goal": str(agent.main_goal_state),
                "plan": [
                    action
                    for time, action in sorted(agent.plans.get(agent.id, {}).items())
                    if action is not None
                ],
                "metrics": agent.get_metrics()
            }
            for agent in problem.agents
        ],
        "domain_actions": len(problem.domain.actions),
        "initial_facts": len(problem.initial_state),
        "goal_facts": len(problem.goal),
        "num_agents": num_agents,
        "num_locations": num_locations,
        "translator_variables": num_locations,
        "translator_derived_variables": 0,
        "translator_facts": translator_facts,
        "translator_goal_facts": len(problem.goal),
        "translator_operators": len(problem.domain.actions),
        "translator_axioms": 0,
        "translator_task_size": translator_facts + len(problem.domain.actions),
    }


class ProblemGenerator:
    def __init__(self, output_dir: str = "problem_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_problem(self, problem: Problem, problem_name: str):
        """Save problem data to JSON file"""
        filename = self.output_dir / f"{problem_name}.json"
        data = _serialize_problem(problem)

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_and_save(self,
                          num_problems: int = 10,
                          min_agents: int = 1,
                          max_agents: int = 50,
                          min_locations: int = 3,
                          max_locations: int = 100):
        """
        Generate and save multiple problems with increasing difficulty.

        Args:
            num_problems: Total number of problems to generate.
            min_agents: Minimum number of agents.
            max_agents: Maximum number of agents.
            min_locations: Minimum number of locations.
            max_locations: Maximum number of locations.
        """
        # Compute step sizes for agents and locations
        agent_step = max(1, (max_agents - min_agents) // num_problems)
        location_step = max(1, (max_locations - min_locations) // num_problems)

        num_agents = min_agents
        num_locations = min_locations

        for i in range(num_problems):
            # Ensure values do not exceed the defined max
            num_agents = min(num_agents, max_agents)
            num_locations = min(num_locations, max_locations)

            # Create problem with unique ID
            problem = generate_problem(num_agents=num_agents, num_locations=num_locations)
            problem_name = f"pb{i + 1}"  # Use pb1, pb2, pb3, etc.

            # Solve and save
            _solve_problem(problem)
            self._save_problem(problem, problem_name)

            # Increment values for the next iteration
            num_agents += agent_step
            num_locations += location_step


def generate_random_connections(locations: List[str], num_undirected_edges: int) -> List[str]:
    """Generates a set of random bidirectional connections between locations"""
    connections = set()
    num_locations = len(locations)
    max_possible = num_locations * (num_locations - 1) // 2
    num_undirected_edges = min(num_undirected_edges, max_possible)

    # Build a spanning tree to ensure connectivity
    shuffled = locations.copy()
    random.shuffle(shuffled)
    connected_nodes = [shuffled[0]]
    remaining = shuffled[1:]

    while remaining:
        loc = random.choice(remaining)
        neighbor = random.choice(connected_nodes)
        connections.add(f"connected({loc}, {neighbor})")
        connections.add(f"connected({neighbor}, {loc})")
        connected_nodes.append(loc)
        remaining.remove(loc)

    # Add remaining edges
    all_pairs = [(loc1, loc2) for i, loc1 in enumerate(locations) for loc2 in locations[i + 1:]
                 if f"connected({loc1}, {loc2})" not in connections]
    random.shuffle(all_pairs)
    needed = num_undirected_edges - (num_locations - 1)
    if needed > 0:
        for loc1, loc2 in all_pairs[:needed]:
            connections.add(f"connected({loc1}, {loc2})")
            connections.add(f"connected({loc2}, {loc1})")

    return list(connections)


def generate_problem(num_agents=2, num_locations=4) -> Problem:
    """Generate a solvable multi-agent movement problem compatible with the A* solver"""

    # Ensure there are at least as many locations as agents
    while num_agents > num_locations:
        num_locations += 1  # Add more locations to match the number of agents

    # Use indexed location names instead of single letters
    locations = [f"loc{i + 1}" for i in range(num_locations)]

    # Domain definitions
    types = {'location': Type('location')}  # TODO: Fix this
    predicates = [
                     Predicate(f'at_agent{aid}', [('?loc', ['location'])]) for aid in range(1, num_agents + 1)
                 ] + [Predicate('connected', [('?from', ['location']), ('?to', ['location'])])]

    # Generate random bidirectional connections between locations
    connections = generate_random_connections(locations, num_locations * 2)

    # Generate schematic actions (not grounded)
    actions = []
    for agent_id in range(1, num_agents + 1):
        actions.append(Action(
            name=f"move_agent{agent_id}",
            signature=[("?from", ["location"]), ("?to", ["location"])],
            precondition={
                Predicate(f"at_agent{agent_id}", [("?from", ["location"])]),
                Predicate("connected", [("?from", ["location"]), ("?to", ["location"])])
            },
            effect=Effect(
                addlist={Predicate(f"at_agent{agent_id}", [("?to", ["location"])])},
                dellist={Predicate(f"at_agent{agent_id}", [("?from", ["location"])])}
            )
        ))

    # Define domain with schematic actions
    domain = Domain(
        name='multi_agent_movement',
        types=types,
        predicates=predicates,
        actions=actions
    )

    # Initial state setup
    initial_state = set()
    for i in range(num_agents):
        # Use Predicate objects with correct signature
        initial_pred = Predicate(f'at_agent{i + 1}', [(locations[i % num_locations], ['location'])])
        initial_state.add(initial_pred)

    # Add connections as Predicate objects
    for conn in connections:
        parts = conn.split('(')[1].split(')')[0].split(', ')
        loc1, loc2 = parts[0], parts[1]
        initial_state.add(Predicate('connected', [(loc1, ['location']), (loc2, ['location'])]))

    # Agent configuration and goals
    agents = []
    final_goals = set()  # To collect the final goals for all agents

    for agent_id in range(1, num_agents + 1):
        start_idx = agent_id - 1
        goal_idx = min(start_idx + 2, num_locations - 1)
        goal_loc = locations[goal_idx]

        # Define the main goal predicate
        main_goal_predicate = Predicate(f'at_agent{agent_id}', [(goal_loc, ['location'])])
        # Create the agent instance
        agent_instance = Agent(
            id=agent_id,
            initial_node=SearchNode(
                projected_state=frozenset({
                    Predicate(f'at_agent{agent_id}', [(locations[start_idx], ['location'])]),
                    *(Predicate('connected', [(locations[i], ['location']), (locations[i + 1], ['location'])])
                      for i in range(num_locations - 1))
                }),
                parent=None,
                action=None,
                h=0,
                g=0,
                agent=None,  # Initially set as None or leave this for the agent
                private_parts=set()
            ),
            public_predicates={f'at_agent{agent_id}', 'connected'},
            domain=domain,
            main_goal_state=frozenset({main_goal_predicate}),
        )

        # Add the agent's initial node information
        agent_instance.initial_node.agent = agent_instance  # Now we assign the actual agent instance

        # Add the agent to the list of agents
        agents.append(agent_instance)

        # Add the agent's final goal to the set of final goals
        final_goals.add(Predicate(f'at_agent{agent_id}', [(goal_loc, ['location'])]))

    # Create problem with agents' initial states
    problem = Problem(
        name=f"{num_agents}agents_{num_locations}locs",
        domain=domain,
        objects={loc: types['location'] for loc in locations},  # Use Type instance here
        init=initial_state,
        goal=final_goals,
        agents=agents
    )

    # Ground actions per agent using multi_agent_ground
    all_tasks = multi_agent_ground(
        agents=problem.agents,
        domain=domain,
        problem_objects=problem.objects,
        remove_statics_from_initial_state=True,
        remove_irrelevant_operators=True
    )

    # Assign pre/post counts to agents
    for agent, task in zip(problem.agents, all_tasks):
        agent.pre_ground_actions = len(domain.actions)  # Pre-grounding count (schematic actions)
        agent.post_ground_actions = len(task.operators)  # Post-grounding count (grounded operators)
        agent.domain.actions = task.operators  # Replace with grounded operators

    return problem


# Example usage
if __name__ == "__main__":
    generator = ProblemGenerator(output_dir="experiment_data")
    generator.generate_and_save(num_problems=25)
    print(f"Generated problems saved to {generator.output_dir}")
