import uuid
import json
from pathlib import Path
import random
from typing import List

from pyperplan.pddl.pddl import Problem, Agent, Type, Predicate, Domain, Action, Effect, SearchNode


class ProblemGenerator:
    def __init__(self, output_dir: str = "problem_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_problem_id(self) -> str:
        return str(uuid.uuid4())

    def _solve_problem(self, problem: Problem):
        """Run the planner for all agents in the problem"""
        for agent in problem.agents:
            agent.start_search(problem)

    def _serialize_problem(self, problem: Problem) -> dict:
        """Convert problem data to JSON-serializable format"""
        return {
            "problem_id": problem.name,
            "domain": problem.domain.name,
            "objects": dict(problem.objects),
            "initial_state": list(problem.initial_state),
            "goal": list(problem.goal),
            "agents": [
                {
                    "id": agent.id,
                    # Extract sorted action names from the plan
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
            "num_agents": len(problem.agents),
            "num_locations": len(problem.objects),
        }

    def _save_problem(self, problem: Problem):
        """Save problem data to JSON file"""
        filename = self.output_dir / f"problem_{problem.name}.json"
        data = self._serialize_problem(problem)

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_and_save(self,
                          num_problems: int = 10,
                          num_agents_range: tuple = (2, 4),
                          num_locations_range: tuple = (4, 8)):
        """
        Generate and save multiple problems with random configurations
        Args:
            num_problems: Number of problems to generate
            num_agents_range: (min, max) agents per problem
            num_locations_range: (min, max) locations per problem
        """
        for _ in range(num_problems):
            # Generate random problem configuration
            num_agents = random.randint(*num_agents_range)
            num_locations = random.randint(*num_locations_range)

            # Create problem with unique ID
            problem = generate_problem(
                num_agents=num_agents,
                num_locations=num_locations
            )
            problem.name = f"{self._generate_problem_id()}_{num_agents}a_{num_locations}l"

            # Solve and save
            self._solve_problem(problem)
            self._save_problem(problem)



def generate_ground_actions(locations: List[str], agent_id: int) -> List[Action]:
    """Generate all possible grounded move actions for an agent based on location connections"""
    actions = []
    for i in range(len(locations) - 1):
        from_loc = locations[i]
        to_loc = locations[i + 1]

        # Create forward action
        actions.append(Action(
            name=f"move_agent{agent_id}_{from_loc}_{to_loc}",
            signature=[],
            precondition={
                f"at_agent{agent_id}({from_loc})",
                f"connected({from_loc}, {to_loc})"
            },
            effect=Effect(
                addlist={f"at_agent{agent_id}({to_loc})"},
                dellist={f"at_agent{agent_id}({from_loc})"}
            )
        ))

        # Create backward action (if bidirectional movement is allowed)
        # actions.append(Action(
        #     name=f"move_agent{agent_id}_{to_loc}_{from_loc}",
        #     signature=[],
        #     precondition={
        #         f"at_agent{agent_id}({to_loc})",
        #         f"connected({to_loc}, {from_loc})"
        #     },
        #     effect=Effect(
        #         add={f"at_agent{agent_id}({from_loc})"},
        #         remove={f"at_agent{agent_id}({to_loc})"}
        #     )
        # ))
    return actions


def generate_problem(num_agents=2, num_locations=4) -> Problem:
    """Generate a solvable multi-agent movement problem compatible with the A* solver"""
    locations = [chr(ord('A') + i) for i in range(num_locations)]

    # Domain definitions
    types = {'location': Type('location')}
    predicates = [
                     Predicate(f'at_agent{aid}', []) for aid in range(1, num_agents + 1)
                 ] + [Predicate('connected', [])]

    # Generate grounded actions for each agent
    actions = []
    for agent_id in range(1, num_agents + 1):
        actions.extend(generate_ground_actions(locations, agent_id))

    domain = Domain(
        name='multi_agent_movement',
        types=types,
        predicates=predicates,
        actions=actions
    )

    # Initial state setup
    initial_state = set()
    for i in range(num_agents):
        initial_state.add(f'at_agent{i + 1}({locations[i]})')
    for i in range(num_locations - 1):
        initial_state.add(f'connected({locations[i]}, {locations[i + 1]})')

    # Agent configuration
    agents = []
    for agent_id in range(1, num_agents + 1):
        start_idx = agent_id - 1
        goal_idx = min(start_idx + 2, num_locations - 1)
        goal_loc = locations[goal_idx]

        agents.append(Agent(
            id=agent_id,
            initial_node=SearchNode(
                projected_state=frozenset({
                    f'at_agent{agent_id}({locations[start_idx]})',
                    *(f'connected({locations[i]}, {locations[i + 1]})'
                      for i in range(num_locations - 1))
                }),
                parent=None,
                action=None,
                h=0,
                g=0,
                agent=agent_id,
                private_parts=set()
            ),
            public_predicates={f'at_agent{agent_id}', 'connected'},
            domain=domain,
            goal_state=frozenset({f'at_agent{agent_id}({goal_loc})'})
        ))

    return Problem(
        name=f"{num_agents}agents_{num_locations}locs",
        domain=domain,
        objects={loc: 'location' for loc in locations},
        init=frozenset(initial_state),
        goal=frozenset().union(*(a.goal_state for a in agents)),
        agents=agents
    )

# Example usage
if __name__ == "__main__":
    generator = ProblemGenerator(output_dir="experiment_data")

    generator.generate_and_save(
        num_problems=10,
        num_agents_range=(2, 5),
        num_locations_range=(4, 20)
    )
    print(f"Generated problems saved to {generator.output_dir}")