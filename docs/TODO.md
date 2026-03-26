

# TODO

## docs
* make presentation bpmn like the camnda one (eg service tasks)

## Camunda
* altri service task
* whats track vehicle in the loop?
* stop fleet tracking?
* convert to service tasks - to implement:
  * reserve vehicle
  * request vehicle information
* disable invoice receipt demo app
* to only use python, remove other scripts (eg those at the start of acme)
* check code (and remove comments):
  * user.py
  * service_tasks.py
* rename config loader/ACME
* reserve vehicle (keep reserved)
* .env works in docker?

## bank
* why exposing on both http and soap?
* `execution { concurrent }` ? not to `exit 0`
* generate wsdl via script automatically in docker (if needed)