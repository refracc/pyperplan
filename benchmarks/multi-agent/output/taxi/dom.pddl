( define ( domain taxi )
( :requirements :conditional-effects :typing )
( :types
	location - object
	agent - object
	taxi - agent
	passenger - agent
	agent-count - object
)
( :constants
	acount-0 - agent-count
)
( :predicates
	( directly-connected ?location0 - location ?location1 - location )
	( at ?agent0 - agent ?location1 - location )
	( in ?passenger0 - passenger ?taxi1 - taxi )
	( empty ?taxi0 - taxi )
	( free ?location0 - location )
	( goal-of ?passenger0 - passenger ?location1 - location )
	( afree )
	( atemp )
	( taken ?agent0 - agent )
	( consec ?agent-count0 - agent-count ?agent-count1 - agent-count )
)
( :action free
  :parameters ( )
  :precondition
	( and
		( atemp )
	)
  :effect
	( and
		( afree )
		( not ( atemp ) )
	)
)
)
