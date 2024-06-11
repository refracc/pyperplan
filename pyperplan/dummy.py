from pyperplan.pddl.pddl import Agent, Type, Predicate, Effect, Domain, Problem, MultiAgentAction

# Define types
object_type = Type('object', None)
agent_type = Type('agent', object_type)
block_type = Type('block', object_type)

# Define predicates
on = Predicate('on', [('x', [block_type]), ('y', [block_type])])
ontable = Predicate('ontable', [('x', [block_type])])
clear = Predicate('clear', [('x', [block_type])])
holding = Predicate('holding', [('a', [agent_type]), ('x', [block_type])])
handempty = Predicate('handempty', [('a', [agent_type])])

# Define actions
pick_up_effect = Effect()
pick_up_effect.add_effect(ontable)
pick_up_effect.add_effect(clear)
pick_up_effect.del_effect(handempty)
pick_up_effect.add_effect(holding)

put_down_effect = Effect()
put_down_effect.del_effect(holding)
put_down_effect.add_effect(clear)
put_down_effect.add_effect(handempty)
put_down_effect.add_effect(ontable)

stack_effect = Effect()
stack_effect.del_effect(holding)
stack_effect.del_effect(clear)
stack_effect.add_effect(clear)
stack_effect.add_effect(handempty)
stack_effect.add_effect(on)

unstack_effect = Effect()
unstack_effect.add_effect(holding)
unstack_effect.add_effect(clear)
unstack_effect.del_effect(clear)
unstack_effect.del_effect(handempty)
unstack_effect.del_effect(on)

pick_up = MultiAgentAction('pick-up', 'agent', [('x', [block_type])], [clear, ontable, handempty], pick_up_effect)
put_down = MultiAgentAction('put-down', 'agent', [('x', [block_type])], [holding], put_down_effect)
stack = MultiAgentAction('stack', 'agent', [('x', [block_type]), ('y', [block_type])], [holding, clear], stack_effect)
unstack = MultiAgentAction('unstack', 'agent', [('x', [block_type]), ('y', [block_type])], [on, clear, handempty],
                           unstack_effect)

# Define agents
agent1 = Agent('agent1', 'agent')
agent2 = Agent('agent2', 'agent')

# Assign private predicates to agents
agent1.add_private_predicate(holding)
agent1.add_private_predicate(handempty)
agent2.add_private_predicate(holding)
agent2.add_private_predicate(handempty)

# Define domain
domain = Domain('blocks', {'object': object_type, 'agent': agent_type, 'block': block_type},
                [on, ontable, clear, holding, handempty], [pick_up, put_down, stack, unstack])

# Define problem (this is a simple example, and you'd typically fill in with actual initial state and goal)
problem = Problem('blockworld', domain, {'block1': block_type, 'block2': block_type},
                  [ontable, clear, handempty], [on])

print(domain)
print(problem)
