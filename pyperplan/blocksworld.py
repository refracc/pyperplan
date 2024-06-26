from pyperplan.grounding import ground
from pyperplan.heuristics.relaxation import hMaxHeuristic
from pyperplan.pddl.pddl import *
from pyperplan.search.a_star import *

agent_type = Type("agent")
block_type = Type("block")

on = Predicate(name="on", signature=[("?x", [block_type]), ("?y", [block_type])])
ontable = Predicate(name="ontable", signature=[("?x", [block_type])])
clear = Predicate(name="clear", signature=[("?x", [block_type])])

holding = Predicate(name="holding", signature=[("?agent", [agent_type]), ("?x", [block_type])], private=True)
handempty = Predicate(name="handempty", signature=[("?agent", [agent_type])], private=True)

pick_up_effect = Effect(
    addlist={holding},
    dellist={ontable, clear, handempty}
)

pick_up_action = Action(
    name="pick-up",
    signature=[("?a", [agent_type]), ("?x", [block_type])],
    precondition=[clear, ontable, handempty],
    effect=pick_up_effect
)

put_down_effect = Effect(
    addlist={clear, handempty, ontable},
    dellist={holding}
)

put_down_action = Action(
    name="put-down",
    signature=[("?a", [agent_type]), ("?x", [block_type])],
    precondition=[holding],
    effect=put_down_effect
)

stack_effect = Effect(
    addlist={Predicate("clear", [("?x", [block_type])]), handempty,
             Predicate("on", [("?x", [block_type]), ("?y", [block_type])])},
    dellist={holding, Predicate("clear", [("?y", [block_type])])}
)

stack_action = Action(
    name="stack",
    signature=[("?a", [agent_type]), ("?x", [block_type]), ("?y", [block_type])],
    precondition=[holding, Predicate("clear", [("?y", [block_type])])],
    effect=stack_effect
)

unstack_effect = Effect(
    addlist={holding, Predicate("clear", [("?y", [block_type])])},
    dellist={Predicate("clear", [("?x", [block_type])]), handempty,
             Predicate("on", [("?x", [block_type]), ("?y", [block_type])])}
)

unstack_action = Action(
    name="unstack",
    signature=[("?a", [agent_type]), ("?x", [block_type]), ("?y", [block_type])],
    precondition=[Predicate("on", [("?x", [block_type]), ("?y", [block_type])]),
                  Predicate("clear", [("?x", [block_type])]),
                  handempty],
    effect=unstack_effect
)

domain = Domain(name="blocksworld", types={agent_type, block_type}, predicates={on, ontable, clear, handempty, holding},
                actions={pick_up_action, put_down_action, stack_action, unstack_action})

public_objects = {
    "a": block_type,
    "b": block_type,
    "c": block_type,
    "d": block_type,
    "e": block_type,
    "f": block_type,
    "g": block_type,
    "h": block_type,
    "i": block_type,
    "j": block_type,
}

# Define private objects (optional)
agents = {
    "a1": agent_type,
    "a2": agent_type,
    "a3": agent_type,
    "a4": agent_type,
}

initial_state = [
    Predicate("handempty", [("a1", agent_type)]),
    Predicate("handempty", [("a2", agent_type)]),
    Predicate("handempty", [("a3", agent_type)]),
    Predicate("handempty", [("a4", agent_type)]),
    Predicate("clear", [("c", block_type)]),
    Predicate("clear", [("f", block_type)]),
    Predicate("ontable", [("i", block_type)]),
    Predicate("ontable", [("f", block_type)]),
    Predicate("on", [("c", block_type), ("e", block_type)]),
    Predicate("on", [("e", block_type), ("j", block_type)]),
    Predicate("on", [("j", block_type), ("b", block_type)]),
    Predicate("on", [("b", block_type), ("g", block_type)]),
    Predicate("on", [("g", block_type), ("h", block_type)]),
    Predicate("on", [("h", block_type), ("a", block_type)]),
    Predicate("on", [("a", block_type), ("d", block_type)]),
    Predicate("on", [("d", block_type), ("i", block_type)]),
]

goal_state = [
    Predicate("on", [("d", block_type), ("c", block_type)]),
    Predicate("on", [("c", block_type), ("f", block_type)]),
    Predicate("on", [("f", block_type), ("j", block_type)]),
    Predicate("on", [("j", block_type), ("e", block_type)]),
    Predicate("on", [("e", block_type), ("h", block_type)]),
    Predicate("on", [("h", block_type), ("b", block_type)]),
    Predicate("on", [("b", block_type), ("a", block_type)]),
    Predicate("on", [("a", block_type), ("g", block_type)]),
    Predicate("on", [("g", block_type), ("i", block_type)]),
]

problem = Problem("bw-1", domain, public_objects, initial_state, goal_state, agents)

print(problem)
print()
print(domain)

grounded_problem = ground(problem)
print(grounded_problem)

solution = astar_search(grounded_problem, heuristic=hMaxHeuristic(grounded_problem))

if solution:
    print("Solution found:")
    for step in solution:
        print(step)
else:
    print("No solution found.")
