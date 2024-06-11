from pyperplan.pddl.pddl import Type, Predicate, Effect, Action, Domain, Problem, Agent
from pyperplan.grounding import ground
from pyperplan.search.a_star import astar_search
from pyperplan.heuristics.relaxation import hMaxHeuristic

# Define types
object_type = Type("object", None)

# Define predicates
holding_predicate = Predicate("holding", [("obj", [object_type])])

# Define effects
pickup_effect = Effect()
pickup_effect.addlist.add(holding_predicate)

putdown_effect = Effect()
putdown_effect.dellist.add(holding_predicate)

# Define actions
pickup_action = Action("pickup", [("obj", [object_type])], [], pickup_effect)
putdown_action = Action("putdown", [("obj", [object_type])], [holding_predicate], putdown_effect)

# Define the domain
domain = Domain("simple_domain", {"object": object_type}, [holding_predicate], [pickup_action, putdown_action])

# Define objects
obj1 = "obj1"
obj2 = "obj2"

# Define initial state
initial_state = [holding_predicate]

# Define goal state
goal_state = [holding_predicate]

# Define the problem
problem = Problem("simple_problem", domain, {obj1: object_type, obj2: object_type}, initial_state, goal_state)

print(problem.__repr__())
print(domain.__repr__())

task = ground(problem)

solution = astar_search(task, heuristic=hMaxHeuristic(task))

print(solution)

# Define some predicates
predicate_at = Predicate('at', [('x', ['location'])])
predicate_has_key = Predicate('has_key', [('x', ['key'])])

# Create agents
robot_agent = Agent('Robot1', 'robot')
human_agent = Agent('Human1', 'human')

# Add private predicates to agents
robot_agent.add_private_predicate(predicate_at)
human_agent.add_private_predicate(predicate_has_key)

# Check if agents know certain predicates
print(robot_agent.knows_predicate(predicate_at))  # True
print(robot_agent.knows_predicate(predicate_has_key))  # False
print(human_agent.knows_predicate(predicate_at))  # False
print(human_agent.knows_predicate(predicate_has_key))  # True

# Print agents to see their private knowledge
print(robot_agent.__repr__())  # Agent(name=Robot1, type=robot, private_predicates={'at[('x', ['location'])]'})
print(human_agent.__repr__())  # Agent(name=Human1, type=human, private_predicates={'has_key[('x', ['key'])]'})
