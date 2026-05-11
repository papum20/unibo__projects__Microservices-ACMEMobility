## ACME

ACME keeps track of some information (see `acme-db.md`)
* storing them (eg vehicle current station) here is the best choice:
  * asking to user isnt good
  * checking coordinates may be imprecise
  * in general, for separation of concerns, other services shouldnt be responsible this

locking:
* user side communicates `stationId` when parking:
  * this is the most reliable way (GPS unreliable and no other service could provide this information)
  * in real life, it would be some one-time code provided by the station
  * ACME still needs to verify the lock is successful with the Stations service; otherwise, it will ask for manual intervention

locking assistance request:
* user can ask for assistance if they have trouble locking the vehicle at the end of the ride
  * ACME proceeds to ending the ride and charging the user
  * at the same time, an operator has been informed and will go physically as soon as possible
  * we assume that the vehicle can only be ridden by the user who rented it, or that, anyway, there is some auto-lock mechanism for the vehicle, so it can be leaved unwatched without risk of theft and the user doesn't have to wait there

## Bank

* `execution { concurrent }`:
  * provides an infinite loop (keep the service running for following operations)
  * can serve multiple users at the same time

## User
By user we mean both the person and his device/app (so, including some information the user doesn't directly know, but the app provides, like codes or ids of vehicles).  

reserve/scan:
* we assume that the user can only pick an available vehicle - the app simply won't show the other ones
