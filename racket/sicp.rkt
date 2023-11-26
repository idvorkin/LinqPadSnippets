#lang racket

; Derivatives are a good example.


; Simplest approach, function in, function out.
(define delta_one 0.0001)
(define (deriv_numerical f)
  ; Derivative is rate of change, rise/run
  (lambda (x) (/ (- (f (+ x delta_one)) (f x)) delta_one)))


; Lets write us a program
(displayln "y(x) = 4* x ^ 2 + 7")
(define (y x)
  (+ 7 (* 4 (* x x))))

(define (y_prime x)
  ((deriv_numerical y) x))

(displayln "y(5)")
(y 5)

(displayln "y_prime(5)")
(y_prime 5)
(displayln "end app")

