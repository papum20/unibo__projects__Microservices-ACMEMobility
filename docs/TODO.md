

# TODO

## docs

## ACME
* save info in db (eg vehicles)
* charging, maintenance status transitions
* check consistency w BPMN (updated)
* db: use all vehicles in env

## Camunda
* reserve vehicle (keep reserved)
* unavailable vehicle status (charging, maintenance)
* general timer? And manual intervention error then, like for too long ride, or user left the vehicle somewhere...

## bank
* why exposing on both http and soap?
* generate wsdl via script automatically in docker (if needed)

## User
* better scripts (params are messy)

## Report
* diagrams:
	* check correctedness (formal coreography)
* tests?:
	* unit tests for each
	* create a **Testing Document** with these scenarios:
		1.  **The Happy Path:** Start rental -> Drive -> Return with 50% battery. *Check: Is the price correct? Is the 10€ sblocked?*
		2.  **The Penalty Path:** Start rental -> Drive -> Return with 10% battery. *Check: Does the system add the 10% penalty to the final bill?*
		3.  **The 30-Minute Rule:** Reserve a vehicle -> Wait 31 minutes (simulated). *Check: Does the system automatically cancel and charge the 10€ deposit?*
		4.  **The Cancellation Path:** Reserve -> Cancel after 2 minutes. *Check: Is it free?* Cancel after 6 minutes. *Check: Is the 10€ charged?*