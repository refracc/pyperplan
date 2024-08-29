( define ( problem blocks-4-0 )
( :domain blocks )
( :objects
	a1 a2 a3 a4 - agent
	a c b e d g f i h k j m l - block
	acount-1 acount-2 acount-3 acount-4 - agent-count
)
( :init
	( handempty a1 )
	( handempty a2 )
	( handempty a3 )
	( handempty a4 )
	( clear j )
	( clear b )
	( ontable f )
	( ontable k )
	( on j e )
	( on e d )
	( on d c )
	( on c a )
	( on a l )
	( on l h )
	( on h g )
	( on g m )
	( on m i )
	( on i f )
	( on b k )
	( afree )
	( consec acount-0 acount-1 )
	( consec acount-1 acount-2 )
	( consec acount-2 acount-3 )
	( consec acount-3 acount-4 )
)
( :goal
	( and
		( on d a )
		( on a e )
		( on e l )
		( on l m )
		( on m c )
		( on c j )
		( on j f )
		( on f k )
		( on k g )
		( on g h )
		( on h i )
		( on i b )
		( afree )
	)
)
)
