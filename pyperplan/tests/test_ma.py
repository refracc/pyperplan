import pytest
from pyperplan.pddl.pddl import *
from queue import Queue


@pytest.fixture
def setup_environment():
    # Define some predicates and states
    predicates = {Predicate('at', [('location', ['A', 'B', 'C'])]),
                  Predicate('connected', [('location1', ['A', 'B']), ('location2', ['B', 'C'])])}

    types = {'location': Type('location')}

    initial_state = {'at(A)', 'connected(A, B)', 'connected(B, C)'}
    goal_state = {'at(C)'}

    domain = Domain(name='test_domain', types=types, predicates=predicates, actions=create_actions())

    agent = Agent(id=1, initial_node=None, public_predicates=predicates, domain=domain, goal_state=goal_state)
    agent.message_queue = Queue()

    return agent, initial_state, goal_state, domain


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


def test_is_applicable(setup_environment):
    _, initial_state, _, domain = setup_environment
    action = domain.actions[0]
    assert action.is_applicable(initial_state)
    assert not action.is_applicable({'at(B)'})


def test_apply_action(setup_environment):
    _, initial_state, _, domain = setup_environment
    action = domain.actions[0]
    new_state = action.apply(initial_state)
    expected_state = {'at(B)', 'connected(A, B)', 'connected(B, C)'}
    assert new_state == expected_state


def test_local_heuristic(setup_environment):
    agent, initial_state, _, _ = setup_environment
    agent.local_heuristic = lambda state: 2  # Mocking heuristic value for testing
    heuristic_value = agent.local_heuristic(initial_state)
    assert heuristic_value == 2


def test_send_message(setup_environment):
    agent, _, _, _ = setup_environment
    recipient = Agent(id=2, initial_node=None, public_predicates=set(), domain=agent.domain,
                      goal_state=agent.goal_state)
    recipient.message_queue = Queue()
    send_message('state', 'test_content', recipient)
    message = recipient.message_queue.get_nowait()
    assert message['type'] == 'state'
    assert message['content'] == 'test_content'


def test_expand(setup_environment):
    agent, initial_state, _, domain = setup_environment
    node = SearchNode(initial_state, None, None, 0, 0, agent.id, None)
    agent.expand(node, False, domain)
    assert len(agent.local_open_list) == 1
    new_node = list(agent.local_open_list)[0]
    assert 'at(B)' in new_node.projected_state


def test_project_action(setup_environment):
    agent, _, _, domain = setup_environment
    action = domain.actions[0]
    projected_preconditions, projected_add_effects, projected_remove_effects, name, _ = action.project(domain, agent)
    print(f"Projected Preconditions: {projected_preconditions}")  # Debug print
    assert 'at(A)' in projected_preconditions
    assert 'connected(A, B)' in projected_preconditions
    assert 'at(B)' in projected_add_effects
    assert 'at(A)' in projected_remove_effects
    assert name == 'move(A, B)'


def test_agent_process_comm(setup_environment):
    agent, initial_state, goal_state, domain = setup_environment
    recipient = Agent(id=2, initial_node=None, public_predicates=set(), domain=domain, goal_state=goal_state)
    recipient.message_queue.put({'type': 'state', 'content': {'state': initial_state, 'uids': [1, 2], 'sender': agent.id, 'heuristic': 2, 'distributed': False}})
    recipient.process_comm()
    assert len(recipient.local_open_list) > 0


if __name__ == '__main__':
    pytest.main()
