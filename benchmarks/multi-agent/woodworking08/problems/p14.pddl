; woodworking task with 12 parts and 120% wood
; Machines:
;   1 grinder
;   1 glazer
;   1 immersion-varnisher
;   1 planer
;   1 highspeed-saw
;   1 spray-varnisher
;   1 saw
; random seed: 48592

(define (problem wood-prob)
  (:domain woodworking)
  (:objects
    green blue red mauve white black - acolour
    beech teak cherry - awood
    p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 - part
    b0 b1 b2 b3 b4 - board
    s0 s1 s2 s3 s4 s5 s6 s7 s8 - aboardsize
	(:private grinder0
		grinder0 - grinder
	)
	
	(:private glazer0
		glazer0 - glazer
	)

	(:private planer0
		planer0 - planer
	)

	(:private immersion-varnisher0
		immersion-varnisher0 - immersion-varnisher
	)

	(:private highspeed-saw0
		highspeed-saw0 - highspeed-saw
	)

	(:private saw0
		saw0 - saw
	)

	(:private spray-varnisher0
		spray-varnisher0 - spray-varnisher
	)
  )
  (:init
    (grind-treatment-change grinder0 varnished colourfragments)
    (grind-treatment-change grinder0 glazed untreated)
    (grind-treatment-change grinder0 untreated untreated)
    (grind-treatment-change grinder0 colourfragments untreated)
    (is-smooth smooth)
    (is-smooth verysmooth)
    (= (total-cost) 0)
    (boardsize-successor s0 s1)
    (boardsize-successor s1 s2)
    (boardsize-successor s2 s3)
    (boardsize-successor s3 s4)
    (boardsize-successor s4 s5)
    (boardsize-successor s5 s6)
    (boardsize-successor s6 s7)
    (boardsize-successor s7 s8)
    (has-colour glazer0 blue)
    (has-colour glazer0 natural)
    (has-colour glazer0 white)
    (has-colour glazer0 green)
    (has-colour glazer0 red)
    (has-colour immersion-varnisher0 blue)
    (has-colour immersion-varnisher0 natural)
    (has-colour immersion-varnisher0 green)
    (has-colour immersion-varnisher0 black)
    (has-colour immersion-varnisher0 white)
    (has-colour immersion-varnisher0 red)
    (empty highspeed-saw0)
    (has-colour spray-varnisher0 blue)
    (has-colour spray-varnisher0 natural)
    (has-colour spray-varnisher0 green)
    (has-colour spray-varnisher0 black)
    (has-colour spray-varnisher0 white)
    (has-colour spray-varnisher0 red)
    (unused p0)
    (goalsize p0 small)
    (= (spray-varnish-cost p0) 5)
    (= (glaze-cost p0) 10)
    (= (grind-cost p0) 15)
    (= (plane-cost p0) 10)
    (available p1)
    (colour p1 blue)
    (wood p1 beech)
    (surface-condition p1 smooth)
    (treatment p1 glazed)
    (goalsize p1 small)
    (= (spray-varnish-cost p1) 5)
    (= (glaze-cost p1) 10)
    (= (grind-cost p1) 15)
    (= (plane-cost p1) 10)
    (unused p2)
    (goalsize p2 large)
    (= (spray-varnish-cost p2) 15)
    (= (glaze-cost p2) 20)
    (= (grind-cost p2) 45)
    (= (plane-cost p2) 30)
    (unused p3)
    (goalsize p3 small)
    (= (spray-varnish-cost p3) 5)
    (= (glaze-cost p3) 10)
    (= (grind-cost p3) 15)
    (= (plane-cost p3) 10)
    (unused p4)
    (goalsize p4 medium)
    (= (spray-varnish-cost p4) 10)
    (= (glaze-cost p4) 15)
    (= (grind-cost p4) 30)
    (= (plane-cost p4) 20)
    (unused p5)
    (goalsize p5 medium)
    (= (spray-varnish-cost p5) 10)
    (= (glaze-cost p5) 15)
    (= (grind-cost p5) 30)
    (= (plane-cost p5) 20)
    (unused p6)
    (goalsize p6 large)
    (= (spray-varnish-cost p6) 15)
    (= (glaze-cost p6) 20)
    (= (grind-cost p6) 45)
    (= (plane-cost p6) 30)
    (unused p7)
    (goalsize p7 large)
    (= (spray-varnish-cost p7) 15)
    (= (glaze-cost p7) 20)
    (= (grind-cost p7) 45)
    (= (plane-cost p7) 30)
    (unused p8)
    (goalsize p8 large)
    (= (spray-varnish-cost p8) 15)
    (= (glaze-cost p8) 20)
    (= (grind-cost p8) 45)
    (= (plane-cost p8) 30)
    (unused p9)
    (goalsize p9 small)
    (= (spray-varnish-cost p9) 5)
    (= (glaze-cost p9) 10)
    (= (grind-cost p9) 15)
    (= (plane-cost p9) 10)
    (unused p10)
    (goalsize p10 medium)
    (= (spray-varnish-cost p10) 10)
    (= (glaze-cost p10) 15)
    (= (grind-cost p10) 30)
    (= (plane-cost p10) 20)
    (unused p11)
    (goalsize p11 medium)
    (= (spray-varnish-cost p11) 10)
    (= (glaze-cost p11) 15)
    (= (grind-cost p11) 30)
    (= (plane-cost p11) 20)
    (boardsize b0 s6)
    (wood b0 beech)
    (surface-condition b0 smooth)
    (available b0)
    (boardsize b1 s6)
    (wood b1 beech)
    (surface-condition b1 rough)
    (available b1)
    (boardsize b2 s8)
    (wood b2 cherry)
    (surface-condition b2 rough)
    (available b2)
    (boardsize b3 s3)
    (wood b3 cherry)
    (surface-condition b3 smooth)
    (available b3)
    (boardsize b4 s5)
    (wood b4 teak)
    (surface-condition b4 rough)
    (available b4)
  )
  (:goal
    (and
      (available p0)
      (wood p0 cherry)
      (surface-condition p0 verysmooth)
      (available p1)
      (colour p1 white)
      (surface-condition p1 verysmooth)
      (available p2)
      (wood p2 beech)
      (surface-condition p2 smooth)
      (available p3)
      (colour p3 blue)
      (wood p3 beech)
      (surface-condition p3 smooth)
      (treatment p3 varnished)
      (available p4)
      (colour p4 black)
      (wood p4 teak)
      (treatment p4 varnished)
      (available p5)
      (colour p5 blue)
      (wood p5 beech)
      (available p6)
      (colour p6 natural)
      (surface-condition p6 verysmooth)
      (available p7)
      (colour p7 white)
      (wood p7 beech)
      (surface-condition p7 verysmooth)
      (treatment p7 glazed)
      (available p8)
      (colour p8 red)
      (surface-condition p8 smooth)
      (available p9)
      (colour p9 red)
      (surface-condition p9 verysmooth)
      (available p10)
      (colour p10 green)
      (wood p10 cherry)
      (available p11)
      (surface-condition p11 verysmooth)
      (treatment p11 glazed)
    )
  )
  (:metric minimize (total-cost))
)
