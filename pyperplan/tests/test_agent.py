import pytest
from pyperplan.pddl.pddl import *


@pytest.fixture
def setup_agent():
    # Mock types, predicates, and actions
    block_type = Type("block")
    agent_type = Type("agent")

    on = Predicate(name="on", signature=[("?x", [block_type]), ("?y", [block_type])])
    ontable = Predicate(name="ontable", signature=[("?x", [block_type])])
    clear = Predicate(name="clear", signature=[("?x", [block_type])])

    holding = Predicate(name="holding", signature=[("?agent", [agent_type]), ("?x", [block_type])], private=True)
    handempty = Predicate(name="handempty", signature=[("?agent", [agent_type])], private=True)

    pick_up_effect = Effect(addlist={holding}, dellist={ontable, clear, handempty})
    pick_up_action = Action(name="pick-up", signature=[("?a", [agent_type]), ("?x", [block_type])],
                            precondition={clear, ontable, handempty}, effect=pick_up_effect)

    put_down_effect = Effect(addlist={clear, handempty, ontable}, dellist={holding})
    put_down_action = Action(name="put-down", signature=[("?a", [agent_type]), ("?x", [block_type])],
                             precondition={holding}, effect=put_down_effect)

    actions = {pick_up_action, put_down_action}
    predicates = {on, ontable, clear, handempty, holding}
    domain = Domain(name="blocksworld", types={block_type, agent_type}, predicates=predicates, actions=actions)

    objects = {"a": block_type, "b": block_type, "c": block_type}
    agents = {"a1": agent_type}

    initial_state = [
        Predicate("handempty", [("a1", agent_type)]),
        Predicate("clear", [("c", block_type)]),
        Predicate("ontable", [("c", block_type)]),
    ]

    goal_state = {Predicate("on", [("a", block_type), ("b", block_type)])}

    problem = Problem(name="test-problem", domain=domain, objects=objects, init=initial_state, goal=goal_state,
                      agents=agents)

    # Create initial node and agent
    initial_node = SearchNode(projected_state=set(initial_state), parent=None, action=None, h=0, g=0, agent="a1",
                              private_parts=set())
    agent = Agent(id="a1", initial_node=initial_node, public_predicates={on, ontable, clear}, domain=domain,
                  goal_state=goal_state)

    return agent, problem


def test_agent_initialization(setup_agent):
    agent, problem = setup_agent
    assert agent.id == "a1"
    assert isinstance(agent.message_queue, Queue)
    assert agent.search_active is True
    assert agent.local_open_list == set()
    assert agent.distributed_open_list == set()
    assert agent.plans == {}


def test_applicable_actions(setup_agent):
    agent, problem = setup_agent
    initial_state = agent.initial_node.projected_state
    applicable_actions = agent.applicable_actions(initial_state, problem.domain)

    assert len(applicable_actions) > 0
    for action in applicable_actions:
        assert isinstance(action, Action)


def test_expand(setup_agent):
    agent, problem = setup_agent
    node = agent.initial_node

    agent.expand(node, distributed=False, domain=problem.domain)

    assert len(agent.local_open_list) > 0
    for new_node in agent.local_open_list:
        assert isinstance(new_node, SearchNode)
        assert new_node.g > node.g


def test_local_heuristic(setup_agent):
    agent, problem = setup_agent
    initial_state = agent.initial_node.projected_state

    heuristic_value = agent.local_heuristic(initial_state)

    assert isinstance(heuristic_value, int)
    assert heuristic_value >= 0


def test_compute_relaxed_plan(setup_agent):
    agent, problem = setup_agent
    initial_state = agent.initial_node.projected_state

    relaxed_plan = agent._compute_relaxed_plan(initial_state)

    assert isinstance(relaxed_plan, list)
    assert all(isinstance(action, Action) for action in relaxed_plan)


def test_goal_reached(setup_agent):
    agent, problem = setup_agent
    goal_state = frozenset(problem.goal)

    assert not agent._goal_reached(agent.initial_node.projected_state)

    # Simulate reaching the goal
    agent.initial_node.projected_state = goal_state
    assert agent._goal_reached(agent.initial_node.projected_state)


def test_process_comm(setup_agent):
    agent, problem = setup_agent

    # Simulate sending a message
    send_message("plan_found", "dummy_plan", agent)
    agent.process_comm(problem)

    assert agent.search_active is False


def test_reconstruct(setup_agent):
    agent, problem = setup_agent

    # Create a dummy node and reconstruct
    dummy_node = SearchNode(projected_state=agent.initial_node.projected_state, parent=None, action=None, h=0, g=0,
                            agent="a1", private_parts=set())
    agent.reconstruct(dummy_node, t=0, sender="a1")

    assert "a1" in agent.plans
    assert 0 in agent.plans["a1"]


def test_message_passing():
    agent1 = Agent("a1", None, set(), None, set())
    agent2 = Agent("a2", None, set(), None, set())

    content = {"state": {"on": [("a", "b")]}}

    agent1.send_message("state", content, agent2)

    assert not agent1.message_queue.empty()
    assert agent2.message_queue.qsize() == 1

    message = agent2.message_queue.get()
    assert message['type'] == "state"
    assert message['content'] == content


def test_start_search():
    initial_state = {Predicate("ontable", [("a", "block")])}
    initial_node = SearchNode(projected_state=initial_state, parent=None, action=None, h=0, g=0, agent="a1",
                              private_parts={})

    action = Action(name="pick-up", signature=[], precondition={Predicate("ontable", [("a", "block")])},
                    effect=Effect(addlist={Predicate("holding", [("a", "block")])},
                                  dellist={Predicate("ontable", [("a", "block")])}))
    domain = Domain(name="blocksworld", types={}, predicates={}, actions=[action])
    goal_state = {Predicate("holding", [("a", "block")])}

    agent = Agent("a1", initial_node, set(), domain, goal_state)

    agent.start_search()

    assert len(agent.local_open_list) > 0
