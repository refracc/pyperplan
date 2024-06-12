from pyperplan.pddl.pddl import Agent, Type, Predicate, Effect, Domain, Problem, MultiAgentAction

# Define types
object_type = Type('object', None)
agent_type = Type('agent', object_type)
block_type = Type('block', object_type)

# Define predicates
on = Predicate('on', [('x', [block_type]), ('y', [block_type])])
ontable = Predicate('ontable', [('x', [block_type])])
clear = Predicate('clear', [('x', [block_type])])
holding = Predicate('holding', [('x', [block_type])], True)
handempty = Predicate('handempty', [], True)

# Define actions
pick_up_effect = Effect([ontable, clear, holding], [handempty])
put_down_effect = Effect([clear, handempty, ontable], [holding])
stack_effect = Effect([clear, handempty, on], [holding, clear])

unstack_effect = Effect()
unstack_effect.add_effect(holding)
unstack_effect.add_effect(clear)
unstack_effect.del_effect(clear)
unstack_effect.del_effect(handempty)
unstack_effect.del_effect(on)

pick_up = MultiAgentAction('pick-up', [('x', [block_type])], [clear, ontable, handempty], pick_up_effect)
put_down = MultiAgentAction('put-down', [('x', [block_type])], [holding], put_down_effect)
stack = MultiAgentAction('stack', [('x', [block_type]), ('y', [block_type])], [holding, clear], stack_effect)
unstack = MultiAgentAction('unstack', [('x', [block_type]), ('y', [block_type])], [on, clear, handempty],
                           unstack_effect)

# Define agents
agent1 = Agent('agent1', 'agent')
agent2 = Agent('agent2', 'agent')

pick_up.add_agent(agent1)
put_down.add_agent(agent2)
stack.add_agent(agent1)
unstack.add_agent(agent2)

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
