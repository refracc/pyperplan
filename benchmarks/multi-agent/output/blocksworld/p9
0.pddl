( DEFINE ( PROBLEM BLOCKS-4-0 )
( :DOMAIN BLOCKS )
( :OBJECTS
	A1 A2 A3 A4 - AGENT
	A C B E D G F I H - BLOCK
	ACOUNT-1 ACOUNT-2 ACOUNT-3 ACOUNT-4 - AGENT-COUNT
)
( :INIT
	( HANDEMPTY A1 )
	( HANDEMPTY A2 )
	( HANDEMPTY A3 )
	( HANDEMPTY A4 )
	( CLEAR C )
	( CLEAR F )
	( ONTABLE C )
	( ONTABLE B )
	( ON F G )
	( ON G E )
	( ON E A )
	( ON A I )
	( ON I D )
	( ON D H )
	( ON H B )
	( AFREE )
	( CONSEC ACOUNT-0 ACOUNT-1 )
	( CONSEC ACOUNT-1 ACOUNT-2 )
	( CONSEC ACOUNT-2 ACOUNT-3 )
	( CONSEC ACOUNT-3 ACOUNT-4 )
)
( :GOAL
	( AND
		( ON G D )
		( ON D B )
		( ON B C )
		( ON C A )
		( ON A I )
		( ON I F )
		( ON F E )
		( ON E H )
		( AFREE )
	)
)
)
