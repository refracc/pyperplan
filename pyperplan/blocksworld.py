from pyperplan.pddl.pddl import *

agent_type = Type("agent")
block_type = Type("block")

on = Predicate(name="on", signature=[("?x", ["block"]), ("?y", ["block"])])
ontable = Predicate(name="ontable", signature=[("?x", ["block"])])
clear = Predicate(name="clear", signature=[("?x", ["block"])])

holding = Predicate(name="holding", signature=[("?agent", ["agent"]), ("?x", ["block"])], private=True)
handempty = Predicate(name="handempty", signature=[("?agent", ["agent"])], private=True)

# Print predicates to verify
print(on)
print(ontable)
print(clear)
print(holding)
print(handempty)

pick_up_effect = Effect(
    addlist={Predicate("holding", [("?a", ["agent"]), ("?x", ["block"])])},
    dellist={
        Predicate("ontable", [("?x", ["block"])]),
        Predicate("clear", [("?x", ["block"])]),
        Predicate("handempty", [("?a", ["agent"])])
    }
)

pick_up_action = Action(
    name="pick-up",
    signature=[("?a", ["agent"]), ("?x", ["block"])],
    precondition=[
        Predicate("clear", [("?x", ["block"])]),
        Predicate("ontable", [("?x", ["block"])]),
        Predicate("handempty", [("?a", ["agent"])])
    ],
    effect=pick_up_effect
)

put_down_effect = Effect(
    addlist={
        Predicate("clear", [("?x", ["block"])]),
        Predicate("handempty", [("?a", ["agent"])]),
        Predicate("ontable", [("?x", ["block"])])
    },
    dellist={Predicate("holding", [("?a", ["agent"]), ("?x", ["block"])])}
)

put_down_action = Action(
    name="put-down",
    signature=[("?a", ["agent"]), ("?x", ["block"])],
    precondition=[Predicate("holding", [("?a", ["agent"]), ("?x", ["block"])])],
    effect=put_down_effect
)

stack_effect = Effect(
    addlist={
        Predicate("clear", [("?x", ["block"])]),
        Predicate("handempty", [("?a", ["agent"])]),
        Predicate("on", [("?x", ["block"]), ("?y", ["block"])])
    },
    dellist={
        Predicate("holding", [("?a", ["agent"]), ("?x", ["block"])]),
        Predicate("clear", [("?y", ["block"])])
    }
)

stack_action = Action(
    name="stack",
    signature=[("?a", ["agent"]), ("?x", ["block"]), ("?y", ["block"])],
    precondition=[
        Predicate("holding", [("?a", ["agent"]), ("?x", ["block"])]),
        Predicate("clear", [("?y", ["block"])])
    ],
    effect=stack_effect
)

unstack_effect = Effect(
    addlist={
        Predicate("holding", [("?a", ["agent"]), ("?x", ["block"])]),
        Predicate("clear", [("?y", ["block"])])
    },
    dellist={
        Predicate("clear", [("?x", ["block"])]),
        Predicate("handempty", [("?a", ["agent"])]),
        Predicate("on", [("?x", ["block"]), ("?y", ["block"])])
    }
)

unstack_action = Action(
    name="unstack",
    signature=[("?a", ["agent"]), ("?x", ["block"]), ("?y", ["block"])],
    precondition=[
        Predicate("on", [("?x", ["block"]), ("?y", ["block"])]),
        Predicate("clear", [("?x", ["block"])]),
        Predicate("handempty", [("?a", ["agent"])])
    ],
    effect=unstack_effect
)

