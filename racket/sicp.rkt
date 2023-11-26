#lang racket

(define delta_one 0.0001)
(define (deriv f)
 ; Derivative is rate of change, rise/run
 (lambda (x) ( / (- (f (+ x delta_one))(f x)) delta_one))
)

(displayln "y(x) = 4* x ^ 2")
(define (y x) (* 4 (* x x)) )

(define (y_prime x) ((deriv y) x))

(displayln "y(5)")
(y 5)

(displayln "y_prime(5)")
((deriv y) 1)
(displayln "end app")
