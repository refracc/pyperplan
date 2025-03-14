from pyperplan.pddl.pddl import *


def create_dummy_problem():
    # Define types
    types = {'location': Type('location')}

    # Define predicates (public: agent's own position and connections)
    predicates = [
        Predicate('at_agent1', [('loc', ['location'])]),
        Predicate('at_agent2', [('loc', ['location'])]),
        Predicate('connected', [('loc1', ['location']), ('loc2', ['location'])])
    ]

    # Define actions for Agent 1
    move_a1_ab = Action(
        name='move_agent1_A_B',
        signature=[('from', 'A'), ('to', 'B')],
        precondition={'at_agent1(A)', 'connected(A, B)'},
        effect=Effect({'at_agent1(B)'}, {'at_agent1(A)'})
    )
    move_a1_bc = Action(
        name='move_agent1_B_C',
        signature=[('from', 'B'), ('to', 'C')],
        precondition={'at_agent1(B)', 'connected(B, C)'},
        effect=Effect({'at_agent1(C)'}, {'at_agent1(B)'})
    )

    # Define actions for Agent 2
    move_a2_bc = Action(
        name='move_agent2_B_C',
        signature=[('from', 'B'), ('to', 'C')],
        precondition={'at_agent2(B)', 'connected(B, C)'},
        effect=Effect({'at_agent2(C)'}, {'at_agent2(B)'})
    )
    move_a2_cd = Action(
        name='move_agent2_C_D',
        signature=[('from', 'C'), ('to', 'D')],
        precondition={'at_agent2(C)', 'connected(C, D)'},
        effect=Effect({'at_agent2(D)'}, {'at_agent2(C)'})
    )

    domain = Domain(
        name='multi_agent_transport',
        types=types,
        predicates=predicates,
        actions=[move_a1_ab, move_a1_bc, move_a2_bc, move_a2_cd]
    )

    # Initial state: Agent1 at A, Agent2 at B, connected A-B-C-D
    initial_state = frozenset({
        'at_agent1(A)',
        'at_agent2(B)',
        'connected(A, B)',
        'connected(B, C)',
        'connected(C, D)'
    })

    # Create agents with individual goals
    agent1 = Agent(
        id=1,
        initial_node=SearchNode(
            projected_state=frozenset({'at_agent1(A)', 'connected(A, B)', 'connected(B, C)'}),
            parent=None,
            action=None,
            h=0,
            g=0,
            agent=1,
            private_parts=set()
        ),
        public_predicates={'at_agent1', 'connected'},
        domain=domain,
        goal_state=frozenset({'at_agent1(C)'})
    )

    agent2 = Agent(
        id=2,
        initial_node=SearchNode(
            projected_state=frozenset({'at_agent2(B)', 'connected(B, C)', 'connected(C, D)'}),
            parent=None,
            action=None,
            h=0,
            g=0,
            agent=2,
            private_parts=set()
        ),
        public_predicates={'at_agent2', 'connected'},
        domain=domain,
        goal_state=frozenset({'at_agent2(D)'})
    )

    # Create problem instance
    problem = Problem(
        name="two_agent_delivery",
        domain=domain,
        objects={'A': 'location', 'B': 'location', 'C': 'location', 'D': 'location'},
        init=initial_state,
        goal=frozenset({'at_agent1(C)', 'at_agent2(D)'}),
        agents=[agent1, agent2]
    )

    return problem


def create_independent_exploration_problem():
    # Define types
    types = {'area': Type('area')}

    # Define predicates
    predicates = [
        Predicate('at_robot1', [('loc', ['area'])]),
        Predicate('at_robot2', [('loc', ['area'])]),
        Predicate('explored', [('loc', ['area'])])
    ]

    # Define actions for Robot1
    move_r1 = Action(
        name='move_robot1',
        signature=[('from', 'area'), ('to', 'area')],
        precondition={'at_robot1(?from)'},
        effect=Effect({'at_robot1(?to)'}, {'at_robot1(?from)'})
    )
    explore_r1 = Action(
        name='explore_robot1',
        signature=[('loc', 'area')],
        precondition={'at_robot1(?loc)', 'not explored(?loc)'},
        effect=Effect({'explored(?loc)'}, set())
    )

    # Define actions for Robot2
    move_r2 = Action(
        name='move_robot2',
        signature=[('from', 'area'), ('to', 'area')],
        precondition={'at_robot2(?from)'},
        effect=Effect({'at_robot2(?to)'}, {'at_robot2(?from)'})
    )
    explore_r2 = Action(
        name='explore_robot2',
        signature=[('loc', 'area')],
        precondition={'at_robot2(?loc)', 'not explored(?loc)'},
        effect=Effect({'explored(?loc)'}, set())
    )

    # Define domain
    domain = Domain(
        name='independent_exploration',
        types=types,
        predicates=predicates,
        actions=[move_r1, explore_r1, move_r2, explore_r2]
    )

    # Initial state
    initial_state = frozenset({
        'at_robot1(Start1)',
        'at_robot2(Start2)',
        'not explored(AreaA)',
        'not explored(AreaB)'
    })

    # Agents
    robot1 = Agent(
        id=1,
        initial_node=SearchNode(
            projected_state=frozenset({'at_robot1(Start1)', 'not explored(AreaA)'}),
            parent=None,
            action=None,
            h=0,
            g=0,
            agent=1,
            private_parts=set()
        ),
        public_predicates={'at_robot1', 'explored'},
        domain=domain,
        goal_state=frozenset({'explored(AreaA)'})
    )

    robot2 = Agent(
        id=2,
        initial_node=SearchNode(
            projected_state=frozenset({'at_robot2(Start2)', 'not explored(AreaB)'}),
            parent=None,
            action=None,
            h=0,
            g=0,
            agent=2,
            private_parts=set()
        ),
        public_predicates={'at_robot2', 'explored'},
        domain=domain,
        goal_state=frozenset({'explored(AreaB)'})
    )

    # Create problem instance
    problem = Problem(
        name="independent_exploration",
        domain=domain,
        objects={'Start1': 'area', 'Start2': 'area', 'AreaA': 'area', 'AreaB': 'area'},
        init=initial_state,
        goal=frozenset({'explored(AreaA)', 'explored(AreaB)'}),
        agents=[robot1, robot2]
    )
    return problem


def create_independent_package_delivery_problem():
    # Define types
    types = {'location': Type('location'), 'package': Type('package')}

    # Define predicates
    predicates = [
        Predicate('at_robot1', [('loc', ['location'])]),
        Predicate('at_robot2', [('loc', ['location'])]),
        Predicate('carrying_robot1', [('pkg', ['package'])]),
        Predicate('carrying_robot2', [('pkg', ['package'])]),
        Predicate('delivered', [('pkg', ['package'])])
    ]

    # Define actions for Robot1
    move_r1 = Action(
        name='move_robot1',
        signature=[('from', 'location'), ('to', 'location')],
        precondition={'at_robot1(?from)'},
        effect=Effect({'at_robot1(?to)'}, {'at_robot1(?from)'})
    )
    pickup_r1 = Action(
        name='pickup_robot1',
        signature=[('pkg', 'package'), ('loc', 'location')],
        precondition={'at_robot1(?loc)', 'not carrying_robot1(?pkg)'},
        effect=Effect({'carrying_robot1(?pkg)'}, set())
    )
    deliver_r1 = Action(
        name='deliver_robot1',
        signature=[('pkg', 'package'), ('loc', 'location')],
        precondition={'carrying_robot1(?pkg)', 'at_robot1(?loc)'},
        effect=Effect({'delivered(?pkg)'}, {'carrying_robot1(?pkg)'})
    )

    # Define actions for Robot2
    move_r2 = Action(
        name='move_robot2',
        signature=[('from', 'location'), ('to', 'location')],
        precondition={'at_robot2(?from)'},
        effect=Effect({'at_robot2(?to)'}, {'at_robot2(?from)'})
    )
    pickup_r2 = Action(
        name='pickup_robot2',
        signature=[('pkg', 'package'), ('loc', 'location')],
        precondition={'at_robot2(?loc)', 'not carrying_robot2(?pkg)'},
        effect=Effect({'carrying_robot2(?pkg)'}, set())
    )
    deliver_r2 = Action(
        name='deliver_robot2',
        signature=[('pkg', 'package'), ('loc', 'location')],
        precondition={'carrying_robot2(?pkg)', 'at_robot2(?loc)'},
        effect=Effect({'delivered(?pkg)'}, {'carrying_robot2(?pkg)'})
    )

    # Define domain
    domain = Domain(
        name='independent_package_delivery',
        types=types,
        predicates=predicates,
        actions=[move_r1, pickup_r1, deliver_r1, move_r2, pickup_r2, deliver_r2]
    )

    # Initial state
    initial_state = frozenset({
        'at_robot1(Start1)',
        'at_robot2(Start2)',
        'not carrying_robot1(PackageA)',
        'not carrying_robot2(PackageB)'
    })

    # Agents
    robot1 = Agent(
        id=1,
        initial_node=SearchNode(
            projected_state=frozenset({'at_robot1(Start1)', 'not carrying_robot1(PackageA)'}),
            parent=None,
            action=None,
            h=0,
            g=0,
            agent=1,
            private_parts=set()
        ),
        public_predicates={'at_robot1', 'carrying_robot1'},
        domain=domain,
        goal_state=frozenset({'delivered(PackageA)'})
    )

    robot2 = Agent(
        id=2,
        initial_node=SearchNode(
            projected_state=frozenset({'at_robot2(Start2)', 'not carrying_robot2(PackageB)'}),
            parent=None,
            action=None,
            h=0,
            g=0,
            agent=2,
            private_parts=set()
        ),
        public_predicates={'at_robot2', 'carrying_robot2'},
        domain=domain,
        goal_state=frozenset({'delivered(PackageB)'})
    )

    # Create problem instance
    problem = Problem(
        name="independent_package_delivery",
        domain=domain,
        objects={'Start1': 'location', 'Start2': 'location', 'LocationX': 'location', 'LocationY': 'location',
                 'PackageA': 'package', 'PackageB': 'package'},
        init=initial_state,
        goal=frozenset({'delivered(PackageA)', 'delivered(PackageB)'}),
        agents=[robot1, robot2]
    )
    return problem


# Run the problem
if __name__ == "__main__":
    print("Solving Problem 1: Dummy Blocks World")
    problem = create_dummy_problem()
    for agent in problem.agents:
        agent.start_search(problem)
        print(f"Agent {agent.id} plan: {agent.plans.get(agent.id)}")
        metrics = agent.get_metrics()
        print(f"Agent {agent.id} metrics: {metrics}")

    print("\n\nSolving Problem 2: Exploration")
    problem = create_independent_exploration_problem()
    for agent in problem.agents:
        agent.start_search(problem)
        print(f"Agent {agent.id} plan: {agent.plans.get(agent.id)}")
        metrics = agent.get_metrics()
        print(f"Agent {agent.id} metrics: {metrics}")

    print("\n\nSolving Problem 3: Package Delivery")
    problem = create_independent_package_delivery_problem()
    for agent in problem.agents:
        agent.start_search(problem)
        print(f"Agent {agent.id} plan: {agent.plans.get(agent.id)}")
        metrics = agent.get_metrics()
        print(f"Agent {agent.id} metrics: {metrics}")
