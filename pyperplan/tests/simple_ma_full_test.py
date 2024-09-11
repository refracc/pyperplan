from pyperplan.pddl.pddl import applicable_actions
from pyperplan.pddl.pddl import *
from pyperplan.ma.node import *


def setup_environment():
    types = {'location': Type('location')}
    predicates = [
        Predicate('at', [('location', ['A', 'B', 'C'])]),
        Predicate('connected', [('location1', ['A', 'B', 'C']), ('location2', ['B', 'C'])])
    ]
    actions = [
        Action('move(A, B)',
               [('from', ['A']), ('to', ['B'])],
               {Predicate('at', [('A', 'location')]), Predicate('connected', [('A', 'location1'), ('B', 'location2')])},
               Effect(addlist={Predicate('at', [('B', 'location')])}, dellist={Predicate('at', [('A', 'location')])})),
        Action('move(B, C)',
               [('from', ['B']), ('to', ['C'])],
               {Predicate('at', [('B', 'location')]), Predicate('connected', [('B', 'location1'), ('C', 'location2')])},
               Effect(addlist={Predicate('at', [('C', 'location')])}, dellist={Predicate('at', [('B', 'location')])}))
    ]
    domain = Domain('travel', types, predicates, actions)
    initial_state = [Predicate('at', [('A', 'location')]),
                     Predicate('connected', [('A', 'location1'), ('B', 'location2')]),
                     Predicate('connected', [('B', 'location1'), ('C', 'location2')])]
    goal_state = frozenset([Predicate('at', [('C', 'location')])])
    agent = Agent(id="1", initial_node=initial_state, public_predicates={'at', 'connected'}, domain=domain,
                  goal_state=goal_state)
    return agent, initial_state, goal_state, domain


def test_predicate_creation():
    pred = Predicate('at', [('location', ['A', 'B', 'C'])])
    assert pred.name == 'at'
    assert pred.signature == [('location', ['A', 'B', 'C'])]


def test_action_creation():
    action = Action('move(A, B)',
                    [('from', ['A']), ('to', ['B'])],
                    {Predicate('at', [('A', 'location')]),
                     Predicate('connected', [('A', 'location1'), ('B', 'location2')])},
                    Effect(addlist={Predicate('at', [('B', 'location')])},
                           dellist={Predicate('at', [('A', 'location')])}))
    assert action.name == 'move(A, B)'
    assert len(action.precondition) == 2
    assert len(action.effect.addlist) == 1
    assert len(action.effect.dellist) == 1


def test_domain_creation():
    domain = Domain('travel',
                    {'location': Type('location')},
                    [Predicate('at', [('location', ['A', 'B', 'C'])]),
                     Predicate('connected', [('location1', ['A', 'B', 'C']), ('location2', ['B', 'C'])])],
                    [Action('move(A, B)',
                            [('from', ['A']), ('to', ['B'])],
                            {Predicate('at', [('A', 'location')]),
                             Predicate('connected', [('A', 'location1'), ('B', 'location2')])},
                            Effect(addlist={Predicate('at', [('B', 'location')])},
                                   dellist={Predicate('at', [('A', 'location')])}))])
    assert domain.name == 'travel'
    assert len(domain.types) == 1
    assert len(domain.predicates) == 2
    assert len(domain.actions) == 1


def test_problem_creation():
    agent, initial_state, goal_state, domain = setup_environment()
    problem = Problem(name="travel_problem",
                      domain=domain,
                      objects={'A': 'location', 'B': 'location', 'C': 'location'},
                      init=initial_state,
                      goal=goal_state,
                      agents=[agent])
    assert problem.name == 'travel_problem'
    assert problem.domain == domain
    assert len(problem.objects) == 3
    assert problem.initial_state == initial_state
    assert problem.goal == goal_state
    assert len(problem.agents) == 1


def test_agent_creation():
    agent, initial_state, goal_state, domain = setup_environment()
    assert agent.id == "1"
    assert agent.goal_state == goal_state
    assert agent.domain == domain
    assert len(agent.public_predicates) == 2


def test_applicable_actions():
    agent, initial_state, goal_state, domain = setup_environment()
    applicable = applicable_actions(initial_state, domain)
    assert len(applicable) > 0
    action_names = {action.name for action in applicable}
    assert 'move(A, B)' in action_names


def test_message_passing():
    agent, initial_state, goal_state, domain = setup_environment()
    initial_node = agent.initial_node
    problem = Problem(name="simple_blocks", domain=domain, objects={"A": "location", "B": "location", "C": "location"},
                      init=initial_state, goal=goal_state, agents=[agent])
    message = {"state": initial_state, "uids": [0], "sender": "1", "distributed": False}
    send_message("state", message, agent)
    agent.process_comm(problem)
    assert len(agent.local_open_list) > 0


def test_state_manager():
    state_manager = StateManager()
    state1 = {'at(A)', 'connected(A, B)'}
    state_manager.add_state(state1)
    assert state_manager.get_state(state1) == state1
    state2 = {'at(B)', 'connected(B, C)'}
    state_manager.add_state(state2)
    assert state_manager.get_state(state2) == state2
    assert state_manager.get_state({'at(C)'}) is None


def test_search_node_creation():
    state = {'at(A)', 'connected(A, B)'}
    node = SearchNode(projected_state=state, parent=None, action=None, h=0, g=0, agent="1", private_parts=[])
    assert node.projected_state == state
    assert node.h == 0
    assert node.g == 0
    assert node.agent == "1"
    assert node.private_parts == []


def test_search_node_hashing():
    state = {'at(A)', 'connected(A, B)'}
    node1 = SearchNode(projected_state=state, parent=None, action=None, h=0, g=0, agent="1", private_parts=[])
    node2 = SearchNode(projected_state=state, parent=None, action=None, h=0, g=0, agent="1", private_parts=[])
    assert node1 == node2
    assert hash(node1) == hash(node2)


def test_solve_problem():
    agent, initial_state, goal_state, domain = setup_environment()
    problem = Problem(name="travel_problem", domain=domain, objects={'A': 'location', 'B': 'location', 'C': 'location'},
                      init=initial_state, goal=goal_state, agents=[agent])

    # Initialize the search
    initial_node = SearchNode(projected_state=initial_state, parent=None, action=None, h=0, g=0, agent="1",
                              private_parts=[])
    agent.local_open_list.add(initial_node)

    while True:
        agent.process_comm(problem)

        if not agent.local_open_list:
            assert False, "No solution found."

        current_node = min(agent.local_open_list, key=lambda node: node.g + node.h)
        agent.local_open_list.remove(current_node)

        if current_node.projected_state == goal_state:
            solution = []
            node = current_node
            while node.parent is not None:
                solution.append(node.action)
                node = node.parent
            solution.reverse()
            assert len(solution) > 0, "Solution should be found."
            break

        applicable = applicable_actions(current_node.projected_state, domain)
        for action in applicable:
            new_state = action.apply(current_node.projected_state)
            new_node = SearchNode(projected_state=new_state, parent=current_node, action=action.name, h=0,
                                  g=current_node.g + 1, agent="1", private_parts=[])
            agent.local_open_list.add(new_node)
