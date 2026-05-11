

# TODO

## docs
* make presentation bpmn like the camunda one (eg service tasks)

## ACME
* additional microservices (e.g. db, for user info, or for reservations)
* save info in db (eg vehicles)
* charging, maintenance status transitions

## Camunda
* reserve vehicle (keep reserved)
* unavailable vehicle status (charging, maintenance)
* general timer? And manual intervention error then, like for too long ride, or user left the vehicle somewhere...

## bank
* why exposing on both http and soap?
* generate wsdl via script automatically in docker (if needed)
* cancelAuth -> convertCaution

## User
* better scripts (params are messy)