import pytest

from pyperplan.pddl.pddl import *


def setup_environment():
    types = {'location': Type('location')}
    predicates = [
        Predicate('at', [('location', ['A', 'B', 'C'])]),
        Predicate('connected', [('location1', ['A', 'B', 'C']), ('location2', ['B', 'C'])])
    ]
    actions = [
        Action('move(A, B)',
               [('from', ['A']), ('to', ['B'])],
               {'at(A)', 'connected(A, B)'},
               Effect({'at(B)'}, {'at(A)'})),
        Action('move(B, C)',
               [('from', ['B']), ('to', ['C'])],
               {'at(B)', 'connected(B, C)'},
               Effect({'at(C)'}, {'at(B)'}))
    ]
    domain = Domain('travel', types, predicates, actions)
    initial_state = frozenset(['at(A)', 'connected(A, B)', 'connected(B, C)'])
    goal_state = frozenset(['at(C)'])
    agent = Agent(id=1, initial_node=None, public_predicates={'at', 'connected'}, domain=domain, goal_state=goal_state)
    problem = Problem(name="travel_problem",
                      domain=domain,
                      objects={'A': 'location', 'B': 'location', 'C': 'location'},
                      init=initial_state,
                      goal=goal_state,
                      agents=[agent])

    return agent, initial_state, goal_state, domain, problem


def create_actions():
    move_action = Action(
        name='move(A, B)',
        signature=[('from', 'location'), ('to', 'location')],
        precondition={'at(A)', 'connected(A, B)'},
        effect=Effect(addlist={'at(B)'}, dellist={'at(A)'})
    )
    move_action_2 = Action(
        name='move(B, C)',
        signature=[('from', 'location'), ('to', 'location')],
        precondition={'at(B)', 'connected(B, C)'},
        effect=Effect(addlist={'at(C)'}, dellist={'at(B)'})
    )
    return [move_action, move_action_2]


def test_is_applicable():
    _, initial_state, _, domain, _ = setup_environment()
    action = domain.actions[0]
    assert action.is_applicable(initial_state)
    assert not action.is_applicable({'at(B)'})


def test_apply_action():
    _, initial_state, _, domain, _ = setup_environment()
    action = domain.actions[0]
    new_state = action.apply(initial_state)
    expected_state = {'at(B)', 'connected(A, B)', 'connected(B, C)'}
    assert new_state == expected_state


def test_local_heuristic():
    agent, initial_state, _, _, _ = setup_environment()
    agent.local_heuristic = lambda state: 2  # Mocking heuristic value for testing
    heuristic_value = agent.local_heuristic(initial_state)
    assert heuristic_value == 2


def test_send_message():
    agent, _, _, _, _ = setup_environment()
    recipient = Agent(id=2, initial_node=None, public_predicates=set(), domain=agent.domain,
                      goal_state=agent.goal_state)
    recipient.message_queue = Queue()
    send_message('state', 'test_content', recipient)
    message = recipient.message_queue.get_nowait()
    assert message['type'] == 'state'
    assert message['content'] == 'test_content'


def test_agent_process_comm():
    agent, initial_state, goal_state, domain, problem = setup_environment()
    recipient = Agent(id=2, initial_node=None, public_predicates=set(), domain=domain, goal_state=goal_state)
    recipient.message_queue.put({'type': 'state',
                                 'content': {'state': initial_state, 'uids': [1, 2], 'sender': agent.id, 'heuristic': 2,
                                             'distributed': False}})
    assert recipient.message_queue.qsize() > 0
    recipient.process_comm(problem)
    assert recipient.message_queue.qsize() == 0


if __name__ == '__main__':
    pytest.main()
