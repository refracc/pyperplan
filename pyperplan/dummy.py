from pyperplan.pddl.pddl import Type, Predicate, Effect, Action, Domain, Problem
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