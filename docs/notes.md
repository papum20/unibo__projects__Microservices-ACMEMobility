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

## Bank

* `execution { concurrent }`:
  * provides an infinite loop (keep the service running for following operations)
  * can serve multiple users at the same time