( DEFINE ( DOMAIN BLOCKS )
( :REQUIREMENTS :CONDITIONAL-EFFECTS :TYPING )
( :TYPES
	AGENT - OBJECT
	BLOCK - OBJECT
	AGENT-COUNT - OBJECT
)
( :CONSTANTS
	ACOUNT-0 - AGENT-COUNT
)
( :PREDICATES
	( ON ?BLOCK0 - BLOCK ?BLOCK1 - BLOCK )
	( ONTABLE ?BLOCK0 - BLOCK )
	( CLEAR ?BLOCK0 - BLOCK )
	( HOLDING ?AGENT0 - AGENT ?BLOCK1 - BLOCK )
	( HANDEMPTY ?AGENT0 - AGENT )
	( AFREE )
	( ATEMP )
	( TAKEN ?AGENT0 - AGENT )
	( CONSEC ?AGENT-COUNT0 - AGENT-COUNT ?AGENT-COUNT1 - AGENT-COUNT )
)
( :ACTION FREE
  :PARAMETERS ( )
  :PRECONDITION
	( AND
		( ATEMP )
	)
  :EFFECT
	( AND
		( AFREE )
		( NOT ( ATEMP ) )
	)
)
)
