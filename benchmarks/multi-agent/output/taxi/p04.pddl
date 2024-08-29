( DEFINE ( PROBLEM TAXI-04 )
( :DOMAIN TAXI )
( :OBJECTS
	G1 G2 G3 C H1 H2 H3 - LOCATION
	T1 T2 T3 - TAXI
	P1 P2 P3 - PASSENGER
	ACOUNT-1 ACOUNT-2 ACOUNT-3 ACOUNT-4 ACOUNT-5 ACOUNT-6 - AGENT-COUNT
)
( :INIT
	( DIRECTLY-CONNECTED G1 C )
	( DIRECTLY-CONNECTED G2 C )
	( DIRECTLY-CONNECTED G3 C )
	( DIRECTLY-CONNECTED C G1 )
	( DIRECTLY-CONNECTED C G2 )
	( DIRECTLY-CONNECTED C G3 )
	( DIRECTLY-CONNECTED C H1 )
	( DIRECTLY-CONNECTED C H2 )
	( DIRECTLY-CONNECTED C H3 )
	( DIRECTLY-CONNECTED H1 C )
	( DIRECTLY-CONNECTED H1 H2 )
	( DIRECTLY-CONNECTED H2 C )
	( DIRECTLY-CONNECTED H2 H1 )
	( DIRECTLY-CONNECTED H2 H3 )
	( DIRECTLY-CONNECTED H3 C )
	( DIRECTLY-CONNECTED H3 H2 )
	( AT T1 G1 )
	( AT T2 G2 )
	( AT T3 G3 )
	( EMPTY T1 )
	( EMPTY T2 )
	( EMPTY T3 )
	( AT P1 H1 )
	( AT P2 H2 )
	( AT P3 H3 )
	( FREE H1 )
	( FREE H2 )
	( FREE H3 )
	( FREE C )
	( GOAL-OF P1 H2 )
	( GOAL-OF P2 H3 )
	( GOAL-OF P3 H1 )
	( AFREE )
	( CONSEC ACOUNT-0 ACOUNT-1 )
	( CONSEC ACOUNT-1 ACOUNT-2 )
	( CONSEC ACOUNT-2 ACOUNT-3 )
	( CONSEC ACOUNT-3 ACOUNT-4 )
	( CONSEC ACOUNT-4 ACOUNT-5 )
	( CONSEC ACOUNT-5 ACOUNT-6 )
)
( :GOAL
	( AND
		( AT T1 G1 )
		( AT T2 G2 )
		( AT T3 G3 )
		( AT P1 H2 )
		( AT P2 H3 )
		( AT P3 H1 )
		( AFREE )
	)
)
)
