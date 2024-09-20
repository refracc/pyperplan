(define (problem p1_6_2_2_2_0) (:domain boxpushing)
(:objects
	a1 a2 - agent
	s1 s2 - smallbox
	m1 m2 - mediumbox
	r1x1 r1x2 r1x3 r1x4 r1x5 r1x6 - location
)
(:init
	(at a1 r1x4)
	(at a2 r1x2)
	(at s1 r1x1)
	(at s2 r1x5)
	(at m1 r1x6)
	(at m2 r1x2)
	(connected r1x1 r1x2)
	(connected r1x2 r1x1)
	(connected r1x2 r1x3)
	(connected r1x3 r1x2)
	(connected r1x3 r1x4)
	(connected r1x4 r1x3)
	(connected r1x4 r1x5)
	(connected r1x5 r1x4)
	(connected r1x5 r1x6)
	(connected r1x6 r1x5)
)
(:goal (and
	(at a1 r1x6)
	(at a2 r1x5)
	(at s1 r1x4)
	(at s2 r1x4)
	(at m1 r1x5)
	(at m2 r1x1)
))
)
