

# TODO

## docs

## ACME

## bank
* why exposing on both http and soap?
*

## Report
* tests?:
	* create a **Testing Document** with these scenarios:
		1.  **The Happy Path:** Start rental -> Drive -> Return with 50% battery. *Check: Is the price correct? Is the 10€ sblocked?*
		2.  **The Penalty Path:** Start rental -> Drive -> Return with 10% battery. *Check: Does the system add the 10% penalty to the final bill?*
		3.  **The 30-Minute Rule:** Reserve a vehicle -> Wait 31 minutes (simulated). *Check: Does the system automatically cancel and charge the 10€ deposit?*
		4.  **The Cancellation Path:** Reserve -> Cancel after 2 minutes. *Check: Is it free?* Cancel after 6 minutes. *Check: Is the 10€ charged?*


## other

*	add stations on map
*	test all, all paths
*	fleets: use db
*	fetch fleet db, vehicle info
*	bash scripts for automatic tests
*	add descriptions to tests
*	error user already rented