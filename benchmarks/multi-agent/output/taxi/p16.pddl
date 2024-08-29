( DEFINE ( PROBLEM TAXI-16 )
( :DOMAIN TAXI )
( :OBJECTS
	G1 G2 G3 C D H1 H2 H3 - LOCATION
	T1 T2 T3 - TAXI
	P1 P2 P3 P4 P5 P6 - PASSENGER
	ACOUNT-1 ACOUNT-2 ACOUNT-3 ACOUNT-4 ACOUNT-5 ACOUNT-6 ACOUNT-7 ACOUNT-8 ACOUNT-9 - AGENT-COUNT
)
( :INIT
	( DIRECTLY-CONNECTED G1 C )
	( DIRECTLY-CONNECTED G1 D )
	( DIRECTLY-CONNECTED G2 C )
	( DIRECTLY-CONNECTED G2 D )
	( DIRECTLY-CONNECTED G3 C )
	( DIRECTLY-CONNECTED G3 D )
	( DIRECTLY-CONNECTED C G1 )
	( DIRECTLY-CONNECTED C G2 )
	( DIRECTLY-CONNECTED C G3 )
	( DIRECTLY-CONNECTED C D )
	( DIRECTLY-CONNECTED C H1 )
	( DIRECTLY-CONNECTED C H2 )
	( DIRECTLY-CONNECTED C H3 )
	( DIRECTLY-CONNECTED D G1 )
	( DIRECTLY-CONNECTED D G2 )
	( DIRECTLY-CONNECTED D G3 )
	( DIRECTLY-CONNECTED D C )
	( DIRECTLY-CONNECTED D H1 )
	( DIRECTLY-CONNECTED D H2 )
	( DIRECTLY-CONNECTED D H3 )
	( DIRECTLY-CONNECTED H1 C )
	( DIRECTLY-CONNECTED H1 D )
	( DIRECTLY-CONNECTED H1 H2 )
	( DIRECTLY-CONNECTED H2 C )
	( DIRECTLY-CONNECTED H2 D )
	( DIRECTLY-CONNECTED H2 H1 )
	( DIRECTLY-CONNECTED H2 H3 )
	( DIRECTLY-CONNECTED H3 C )
	( DIRECTLY-CONNECTED H3 D )
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
	( AT P4 D )
	( AT P5 G3 )
	( AT P6 H1 )
	( FREE H1 )
	( FREE H2 )
	( FREE H3 )
	( FREE C )
	( FREE D )
	( GOAL-OF P1 H2 )
	( GOAL-OF P2 H3 )
	( GOAL-OF P3 C )
	( GOAL-OF P4 C )
	( GOAL-OF P5 D )
	( GOAL-OF P6 H3 )
	( AFREE )
	( CONSEC ACOUNT-0 ACOUNT-1 )
	( CONSEC ACOUNT-1 ACOUNT-2 )
	( CONSEC ACOUNT-2 ACOUNT-3 )
	( CONSEC ACOUNT-3 ACOUNT-4 )
	( CONSEC ACOUNT-4 ACOUNT-5 )
	( CONSEC ACOUNT-5 ACOUNT-6 )
	( CONSEC ACOUNT-6 ACOUNT-7 )
	( CONSEC ACOUNT-7 ACOUNT-8 )
	( CONSEC ACOUNT-8 ACOUNT-9 )
)
( :GOAL
	( AND
		( AT T1 G1 )
		( AT T2 G2 )
		( AT T3 G3 )
		( AT P1 H2 )
		( AT P2 H3 )
		( AT P3 C )
		( AT P4 C )
		( AT P5 D )
		( AT P6 H3 )
		( AFREE )
	)
)
)
