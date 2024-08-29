( define ( domain blocks )
( :requirements :conditional-effects :typing )
( :types
	agent - object
	block - object
	agent-count - object
)
( :constants
	acount-0 - agent-count
)
( :predicates
	( on ?block0 - block ?block1 - block )
	( ontable ?block0 - block )
	( clear ?block0 - block )
	( holding ?agent0 - agent ?block1 - block )
	( handempty ?agent0 - agent )
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
