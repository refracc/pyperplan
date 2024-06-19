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
    addlist={holding},
    dellist={ontable, clear, handempty}
)

pick_up_action = Action(
    name="pick-up",
    signature=[("?a", ["agent"]), ("?x", ["block"])],
    precondition=[clear, ontable, handempty],
    effect=pick_up_effect
)

put_down_effect = Effect(
    addlist={clear, handempty, ontable},
    dellist={holding}
)

put_down_action = Action(
    name="put-down",
    signature=[("?a", ["agent"]), ("?x", ["block"])],
    precondition=[holding],
    effect=put_down_effect
)

stack_effect = Effect(
    addlist={Predicate("clear", [("?x", ["block"])]), handempty,
             Predicate("on", [("?x", ["block"]), ("?y", ["block"])])},
    dellist={holding, Predicate("clear", [("?y", ["block"])])}
)

stack_action = Action(
    name="stack",
    signature=[("?a", ["agent"]), ("?x", ["block"]), ("?y", ["block"])],
    precondition=[holding, Predicate("clear", [("?y", ["block"])])],
    effect=stack_effect
)

unstack_effect = Effect(
    addlist={holding, Predicate("clear", [("?y", ["block"])])},
    dellist={Predicate("clear", [("?x", ["block"])]), handempty,
             Predicate("on", [("?x", ["block"]), ("?y", ["block"])])}
)

unstack_action = Action(
    name="unstack",
    signature=[("?a", ["agent"]), ("?x", ["block"]), ("?y", ["block"])],
    precondition=[Predicate("on", [("?x", ["block"]), ("?y", ["block"])]), Predicate("clear", [("?x", ["block"])]),
                  handempty],
    effect=unstack_effect
)
