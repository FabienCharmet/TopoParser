;;;; -*- Mode: Lisp; Syntax: Common-lisp; Package: SNARK -*-

;;;; File: setlink.lisp

(load "snark-system.lisp")
(make-snark-system)

;;;; -*- Mode: Lisp; Syntax: Common-lisp; Package: SNARK -*-

;;;; File: setlink.lisp

(in-package :snark-user)



(setq evaluables '((* numberp 1)(+ numberp 0)))   ;;;?needed


;;;;   some utility functions....

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;   UTILITY FUNCTIONS   ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun snark::make-and-freeze-variable (&optional (sort (snark::top-sort)) number)
  (let ((v (snark::make-variable sort number)))
    (push v snark::*frozen-variables*)
    v))

(defun find-all (var exp &rest args 

		 &key (num-answers 10) (time-limit 20) print-derived print-proof

		 &allow-other-keys) ;; 


  (setq show-patient-id-list nil)

  (let* ((set-of-var (if (eq (first exp) 'set-of-all)

			 (second exp)

			 nil))

	 (exp (if set-of-var

		  `(exists ,(second exp) ,(third exp))

		  exp))

	 (num-answers (if set-of-var 2000 num-answers))

	 (time-limit (if set-of-var 40 time-limit)))

    (run-time-limit time-limit)

    (with-no-output-test

	print-derived

      (progn

	(new-row-context) ;;;added for ambiguous queries

	(apply #'prove 

	       (print (or exp 'false))

	       :answer `(ans ,var)

	       :num-answers num-answers

	       :time-limit time-limit

	       :allow-other-keys t

	       args)

	))


	(and print-proof (print (proof-string)))

    ;;(PRINT (format nil "answer = ~A" (answer-to-lisp (answer))))

    (with-no-output-test

	print-derived

      (if (eql false (answer-to-lisp (answer)))

	  (append (list (cons :answer-vars (cdr var))

			(cons :form exp)

			(cons :answers 

			      (list (list (cons :answer 

						(make-vars (cdr var)))

					  (cons :proof (list "inconsistent assertions"

							     (proof-string)))))))
		  )

	  (if set-of-var

	      (set-of-var 

	       set-of-var

	       (append (list (cons :answer-vars (cdr var))

			     (cons :answers (all-answers 2000 1 print-derived))

			     (cons :form exp))

		       ))

	      (append (list (cons :answer-vars (cdr var))

			    (cons :answers (all-answers num-answers 1 print-derived))

			    (cons :form exp))

		      ))))))


(defun all-answers (&optional (num-answers 1) (index 1) print-derived)

  (and (proof)

	(cons (list (cons :answer 

			  (let ((ans (simplify-answer (term-to-lisp (answer)))))

			    (if (atom ans)

				 ans

			       (let* ((spread (spread-conditional ans)))

				 (if (atom (second spread))

				     spread

				   (cdr (second spread)))))))

		    (cons :proof (proof-string)))

	      (and (or (null num-answers) (< index num-answers))

		   (let ((val-of-closure (closure)))

		     (if (and (neq val-of-closure :agenda-empty )

			      (neq val-of-closure :run-time-limit))			 

			 (all-answers num-answers (+ 1 index))

			 ))))))



(defun spread-conditional (ans)

  (if (eq (car ans) 'answer-if)

      (let* ((args (cdr ans))

	     (if-part (first args))

	     (then-part (spread-conditional (second args)))

	     (else-part (spread-conditional (third args))))

	(if (and (eq (first then-part) 'ans)

		 (eq (first (second then-part)) 'tuple)

		 (eq (first else-part) 'ans)

		 (eq (first (second else-part)) 'tuple))

	    (let* ((then-args (rest (second then-part)))

		   (else-args (rest (second else-part))))

	      `(ans (tuple 

		     ,@(mapcar #'(lambda (x y) `(answer-if ,if-part ,x ,y))

			       then-args else-args))))

	  ans))

      ans))


(defun proof-string ()

 (and (proof)

         (snark::let-options ((print-final-rows t))

             (with-output-to-string

		   (*standard-output*)

		   (snark::print-final-row (proof))) )))



(defmacro with-no-output-test (print-derived &body forms)

  `(if ,print-derived (progn ,@forms) (with-no-output ,@forms)))


(defun another ()

  (closure)

  (if (proof) (simplify-answer (answer-to-lisp (answer)))))


(defun answer-to-lisp (ansatom)

  (if (proof)

      (if (eq (answer) FALSE)    ;;;contradiction in axioms

          ansatom

        (term-to-lisp (answer)))

      :none))


(defun simplify-answer (ans &key inputs)

  (if (atom ans)

      (if (member ans evaluables)

          (simplify-answer (eval ans) :inputs inputs)

        ans)    ;;;; (if (ratiop ans) (float ans) ans) ;;but floating-point answer didnt print

      (if (member (car ans) inputs) ;;; translate skolem function inputs into constants

	  (car ans)

	  (let ((triple (assoc (car ans) evaluables)))

      (if triple

          (destructuring-bind 

           (op type-pred identity) 

           triple

           (accumulate-answer op type-pred identity (cdr ans)))

        (mapcar #'(lambda (ans1) (simplify-answer ans1 :inputs inputs)) ans)

        )))))



(defun simplify-answers ()

  (mapcar #'(lambda (ans) (simplify-answer (term-to-lisp ans))) (answers)))


(defun accumulate-answer (op type-pred identity arg-list)

  (let ((computed-ans identity)

        (symbolic-ans nil))

    (dolist (arg1 arg-list)

      (let ((arg1 (simplify-answer arg1)))

        (if (funcall type-pred arg1)

            (setf computed-ans (funcall op arg1 computed-ans))

          (push arg1 symbolic-ans))))

    (if symbolic-ans

        (cons op (cons 

                  (if (ratiop computed-ans) (float computed-ans) computed-ans)

                  symbolic-ans))

	computed-ans)))


(defun test-temporal-charmet ()
  (initialize)


  (declare-time-relations :intervals t :points t :dates t)
  (declare-relation '$$time-pp-before :any  :new-name 'before
		    :allowed-in-answer nil )
  (declare-relation '$$time-pp-after :any  :new-name 'after
		    :allowed-in-answer nil )
  (use-resolution)
  (use-paramodulation)
  (assert-supported nil)
  (use-literal-ordering-with-resolution 'literal-ordering-p) ;;
;;; a search strategy that allows us to prefer to unify on replation symbol before another

  (ordering-functions>constants t)
;;; if a complex term and a constant are equal, we prefer to replace the complex term with the simple constant.



  (print-rows-when-derived :print) ;;;; print steps in proof search as they are deduced.
  (print-rows-when-processed nil)  ;;;more detailed printing;;
;;; use (print-rows-when-processed :print) to turn it on.


  (trace-rewrite nil)
  (rewrite-answers t)
;;; simplfy the answers if possible

  (use-conditional-answer-creation t) ;;;  t to avoid disjunctive answers

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;     DECLARATIONS      ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


;;; INSERT TYPES HERE ;;;

  (declare-snark-option time-point-sort-name 'time-point 'time-point)
  (declare-time-relations :intervals t :points t :dates t)

  (declare-function '$$cons 2 :new-name 'cons)
  (declare-function '$$list :any  :new-name 'list)
  (declare-constant '$$nil :alias 'nil :sort 'list)


;;; a time-point is before another
  (declare-relation 'snark::$$time-pp 3 :allowed-in-answer nil )
;'(declare-relation '$$time-pp-before :any  :new-name 'before :allowed-in-answer nil )

  (declare-relation 'before= 2 :sort '((1 time-point)(2 time-point)) :allowed-in-answer nil)     
;;; to avoid conditional answers with before.
;;; a time-point is before or equal to another

  (declare-time-relations :intervals t :points t :dates t)

  (declare-relation 'non-empty 1 :sort '((1 time-interval)))

  (declare-function 'make-interval 2
		    :sort '(time-interval (1 time-point) (2 time-point)))
;;; the interval between two time-points

  (declare-function 'intersection 2 :sort '(time-interval (t time-interval))
		    :commutative t
		    :allowed-in-answer nil)
;;; the intersection of two time intervals.

  (declare-function 'max-time :any :sort '(time-point (t time-point))
                    :commutative t
                    :allowed-in-answer nil)
;;; the later of two time-points


  (declare-function 'min-time :any :sort '(time-point (t time-point))
                    :commutative t  
                    :allowed-in-answer nil)
;;; the earlier of two time-points


  (declare-relation 'setlink0 3 :sort '((1 node) (2 node) (3 time-interval)))
;;; two nodes are linked directly within a given time-interval
;;; they may be linked at other times too.

  (declare-relation 'setlink 3 :sort '((1 node) (2 node) (3 time-interval)))
;;;  two nodes are linked, directly or indirectly within a time interval;
;;;  we regard a node as not always being linked to itself.

  (declare-relation 'data-confidentiality 2 :sort '((1 data) (2 time-interval))
		    :allowed-in-answer nil)  ;;; to avoid conditional answers that test data-confidentiality.
;;; the data-confidentiality of a

  (declare-relation 'node-confidentiality 2 :sort '((1 user) (2 time-interval))
		    :allowed-in-answer nil)  ;;; to avoid conditional answers that test data-confidentiality.
;;; the data-confidentiality of a

  (declare-relation 'data-at-node 3 :sort '((1 data) (2 node) (3 time-interval)))
  ;;; <data> is stored at <node> during <time-interval>

  (declare-relation 'data-readable 3 :sort '((1 data) (2 node) (3 time-interval)))
;;; <data> is readable from <node> during <time-interval>
  
  (declare-relation 'reads 3 :sort '((1 user) (2 data) (3 time-interval)))
;;;  <user> can read <data> during <time interval>

  (declare-relation 'access 3 :sort '((1 user) (2 node) (3 time-interval)))
;;;  <user> access <node> during <time interval>

  (declare-relation 'reads-at-node 4 :sort '((1 user) (2 data) (3 node) (4 time-interval)))
;;; <user> can read <data> at <node> during <time-interval>

  (declare-relation 'data-isauthorized 3 :sort '((1 user) (2 data) (3 time-interval)))
;;; a user is authorized to read a data during a time interval

  (declare-relation 'node-isauthorized 3 :sort '((1 user) (2 node) (3 time-interval)))
;;; a user is authorized to read a data during a time interval

;;; relation ordering strategy

  (declare-ordering-greaterp 'setlink0 'setlink) ;;; always resolve 'setlink0 before 'setlink in a given clause.
  (declare-ordering-greaterp 'setlink 'data-at-node '= 'snark::$$time-pp) ;;
  (declare-ordering-greaterp 'data-confidentiality 'snark::$$time-pp)
  (declare-ordering-greaterp 'data-confidentiality 'reads)
  (declare-ordering-greaterp 'data-confidentiality 'data-isauthorized)
  (declare-ordering-greaterp 'intersection 'make-interval)
  (declare-ordering-greaterp 'intersection 'max-time)
  (declare-ordering-greaterp 'intersection 'min-time)
  (declare-ordering-greaterp 'reads '= 'non-empty)

;;;   (assert '(setlink ?n.node ?n.node ?t.time-interval) :name 'setlink-is-reflexive)
;;; a node is always linked to itself.---decided to omit.

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;   SETLINK FUNCTIONS   ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  (assert '(not (setlink0 ?n.node ?n.node ?t.time-interval)) :name 'setlink0-is-irreflexive)
  ;; a node is not directly linked to itself.

  (assert
   '(implied-by
     (setlink ?x.node ?y.node ?t.time-interval)
     (setlink0 ?x.node ?y.node ?t.time-interval))
   :sequential :uninherited
   :name 'setlink-if-setlink0)
;;; two nodes are connected if they are directly connected.


  (assert
   '(implied-by
     (setlink ?x.node ?z.node
      (make-interval ?t1.time-point ?t2.time-point))
     (and
      (=
       (make-interval ?t1.time-point ?t2.time-point)
       (intersection
	(make-interval ?r1.time-point ?r2.time-point)
	(make-interval ?s1.time-point ?s2.time-point)))
      (setlink0 ?x.node ?y.node (make-interval ?r1.time-point ?r2.time-point))
      (setlink ?y.node ?z.node (make-interval ?s1.time-point ?s2.time-point)))
     )
   :sequential :uninherited
   :name 'transitivity-connectivity)

;;; if node x is connected to node y during  time interval r, and
;;;    node y is connected to node z during time interval s,
;;; then node x is connected to node z during the intersection of the two time intervals.
;;;

  (assert
   '(implied-by
     (data-readable ?d.data ?n2.node ?t.time-interval)
     (and
      (= ?t.time-interval (intersection ?r.time-interval ?s.time-interval))
      (data-at-node ?d.data ?n1.node ?r.time-interval)
      (setlink ?n1.node ?n2.node ?s.time-interval)
      (non-empty ?t.time-interval)))
   :sequential :uninherited
   :name 'data-readable-if-linked-to-data-at-node)

  ;;; if data is readable at node n1, and node n1 is connected to node n2,
  ;;; then the data is also readable at node n2, provided the time intervals are compatible.

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;    CONFIDENTIALITY    ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  '(assert
   '(iff
     (data-confidentiality ?d.data ?t.time-interval)
     (forall ((?u.user  :conc-name some-user))
      (or 
       (not (reads ?u.user ?d.data ?t.time-interval))
       (data-isauthorized ?u.user ?d.data ?t.time-interval)))
     )
   :name 'data-confidentiality
   :sequential :uninherited
   )

   (assert
    '(iff
      (data-confidentiality ?d.data ?t.time-interval)
      (forall ((?u.user  :conc-name some-user))
      (and
 	(= ?t.time-interval (intersection ?r.time-interval ?s.time-interval))
        (or 
         (not (reads ?u.user ?d.data ?r.time-interval))
         (isauthorized ?u.user ?d.data ?s.time-interval ))
       )
      )
      )
    :name 'data-confidentiality
    :sequential :uninherited
    )

  (assert
   '(iff
     (node-confidentiality ?u.user ?t.time-interval)
     (forall ((?u.user  :conc-name some-user))
     (and
       (data-confidentiality ?d.data ?t.time-interval)
       (data-at-node ?d.data ?n.node ?t.time-interval)
       (or 
        (not (access ?u.user ?n.node ?t.time-interval))
        (node-isauthorized ?u.user ?n.node ?t.time-interval)
       )
      )
     )
    )
   :name 'node-confidentiality
   :sequential :uninherited
  )

;  (assert
;   '(implied-by
;     (reads ?u.user ?d.data ?t.time-interval)
;     (and
;      (exists ((?n.node :conc-name some-node))
;       (and
;	(data-readable ?d.data ?n.node ?t.time-interval)
;	(reads-at-node ?u.user ?d.data ?n.node ?t.time-interval))
;       )))
;  :sequential :uninherited
;  :name :reads-if-reads-readable-data-at-some-node)

;;; user u can read data d provided that there is a node n such that
;;; d is readable at n and u reads d at n




;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;     TIME FUNCTIONS    ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  (assert
   '(iff
    (non-empty (make-interval ?t1.time-point ?t2.time-point))
     (before ?t1.time-point ?t2.time-point))
   :sequential :uninherited
   :name 'non-empty-if-time-points-ordered)

  (assert-rewrite
   '(=
     (intersection
      (make-interval ?r1.time-point ?r2.time-point)
      (make-interval ?s1.time-point ?s2.time-point))
     (make-interval
      (max-time ?r1.time-point ?s1.time-point)
      (min-time ?r2.time-point ?s2.time-point)))
   :name 'intersection-commutes-with-make-interval)
;;;; the intersection of two time intervals is the time interval
;;;   whose start point is the max of the start points of the two given intervals, and
;;;  whose finish point is the min of the finish points of the two givien intervals.

  (assert
   '(implied-by
     (= (max-time ?t1.time-point ?t2.time-point) ?t2.time-point)
     (before ?t1.time-point ?t2.time-point))
   :sequential :uninherited
   :name 'max-if-after)
;;; the max of two time-points is the later of the two

  (assert
   '(implied-by
     (= (min-time ?t1.time-point ?t2.time-point) ?t1.time-point)
     (before ?t1.time-point ?t2.time-point))
   :sequential :uninherited
   :name 'min-if-before)
  ;; the min of two time-points is the earlier of the two.


  (assert '(= (max-time ?t.time-point ?t.time-point) ?t.time-point)
	  :name 'max-xx-is-x)
;;; the max of two equal time points is either of them.

  (assert '(= (min-time ?t.time-point ?t.time-point) ?t.time-point)
	  :name 'min-xx-is-x)
;;; the min of two equal time-points is either of them.


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;         FACTS         ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;; INSERT NODES HERE ;;;

;;; INSERT TIME POINTS HERE ;;;

;;; INSERT DATA HERE ;;;

;;; INSERT USER HERE ;;;

;;; INSERT SETLINK HERE ;;;

;;; INSERT DATA-ISAUTHORIZED HERE ;;;

;;; INSERT READS HERE ;;;

;(declare-constant 'mylist :sort 'list)
;(setq mylist (cons 'node-a (cons 'node-b (cons 'node-c '()))))



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;  CLOSED-WORLD ASSUMPTIONS  ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


  (assert '(implies
	   (reads ?u.user ?d.data ?t.time-interval)
	   (or (= ?u.user user-1)(= ?u.user user-2)))  ;;; 
	 :sequential :uninherited
	 :name 'closed-world-assumption-for-reads)

  (assert '(implies
	   (isauthorized ?u.user ?d.data ?t.time-interval)
	   (or (= ?u.user user-1)(= ?u.user user-2)))   ;;; 
	 :sequential :uninherited
	 :name 'closed-world-assumption-for-is-authorized)

  (assert '(implies
	   (not (isauthorized ?u.user ?d.data ?t.time-interval))
	   (or (= ?u.user user-1)(= ?u.user user-2)))   ;;; (= ?u.user user-1) (= ?u.user user-2)
	 :sequential :uninherited
    :name 'closed-world-assumption-for-not-is-authorized)

 
  (assert '(implies
	   (not (data-confidentiality ?d.data ?t.time-interval))
	   (or (= ?d.data data-1)))   ;;;(= ?d.data data-2)
	 :sequential :uninherited
	 :name 'closed-world-assumption-for-not-data-confidentiality)
 


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;       QUESTIONS       ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  (find-all '(ans  ?t.time-interval)
    '(and
       (data-confidentiality data-1 ?t.time-interval)   
       (non-empty ?t.time-interval)
       )
	   :name 'data-confidentiality-maintained-conjecture
	   :num-answers 1
	   :time-limit 1
   :print-derived :print)

  (answers)

  


  )
