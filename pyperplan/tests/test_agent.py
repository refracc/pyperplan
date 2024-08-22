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
    agents = [agent_type]

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


def test_applicable_actions():
    action = Action(
        name="pick-up",
        signature=[],
        precondition={Predicate("ontable", [("a", "block")])},
        effect=Effect(
            addlist={Predicate("holding", [("a", "block")])},
            dellist={Predicate("ontable", [("a", "block")])}
        )
    )

    domain = Domain(name="blocksworld", types={}, predicates={
        Predicate("ontable", [("a", "block")]),
        Predicate("holding", [("a", "block")])
    }, actions=[action])

    initial_state = {Predicate("ontable", [("a", "block")])}
    agent = Agent(id="a1", initial_node=None, public_predicates=set(), domain=domain, goal_state=set())

    applicable_actions = agent.applicable_actions(initial_state, domain)

    print("Applicable Actions:", applicable_actions)  # Debug print

    assert len(applicable_actions) > 0


def test_expand():
    initial_state = {Predicate("ontable", [("a", "block")])}
    initial_node = SearchNode(projected_state=initial_state, parent=None, action=None, h=0, g=0, agent="a1",
                              private_parts={})

    action = Action(name="pick-up", signature=[], precondition={Predicate("ontable", [("a", "block")])},
                    effect=Effect(addlist={Predicate("holding", [("a", "block")])},
                                  dellist={Predicate("ontable", [("a", "block")])}))

    domain = Domain(name="blocksworld", types={}, predicates={
        Predicate("ontable", [("a", "block")]),
        Predicate("holding", [("a", "block")])}, actions=[action])
    goal_state = {Predicate("holding", [("a", "block")])}

    agent = Agent(id="a1", initial_node=initial_node, public_predicates=set(), domain=domain, goal_state=goal_state)

    agent.expand(initial_node, distributed=False, domain=domain)

    assert len(agent.local_open_list) > 0


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
    # Setup initial state and node
    initial_state = {Predicate("ontable", [("a", "block")])}
    initial_node = SearchNode(
        projected_state=initial_state,
        parent=None,
        action=None,
        h=0,
        g=0,
        agent="a1",
        private_parts={}
    )

    # Define action, domain, and goal state
    action = Action(
        name="pick-up",
        signature=[],
        precondition={Predicate("ontable", [("a", "block")])},
        effect=Effect(
            addlist={Predicate("holding", [("a", "block")])},
            dellist={Predicate("ontable", [("a", "block")])}
        )
    )

    domain = Domain(
        name="blocksworld",
        types={},
        predicates={
            Predicate("ontable", [("a", "block")]),
            Predicate("holding", [("a", "block")])
        },
        actions=[action]
    )

    goal_state = {Predicate("holding", [("a", "block")])}

    # Initialize the agent
    agent = Agent(
        id="a1",
        initial_node=initial_node,
        public_predicates=set(),
        domain=domain,
        goal_state=goal_state
    )

    # Setup the problem
    problem = Problem(
        name="simple_blocks",
        domain=domain,
        objects={"a": "block"},
        init=initial_state,
        goal=goal_state,
        agents={"a1": agent}
    )

    # Define a message to send
    message = {
        "state": initial_state,
        "uids": [0],
        "sender": "a1",
        "distributed": False
    }

    # Mock send_message to directly add messages to the queue
    def send_message(message_type, message_content, target_agent):
        target_agent.message_queue.put({"type": message_type, "content": message_content})

    # Ensure message structure is correct and process
    send_message("state", message, agent)
    agent.process_comm(problem)

    # Directly check if the local_open_list has entries
    assert len(agent.local_open_list) > 0
