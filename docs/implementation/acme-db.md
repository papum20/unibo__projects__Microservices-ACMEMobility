# ACME DataBase

* `Users`:
  * `userId` (String): Unique identifier for each user
  * `username` (String): the user's name
  * `savedCard` (String): saved payment card
* `Vehicles`:
  * `vehicleId` (String): Unique identifier for each vehicle
  * `status` (String): current status (available, reserved, rented, maintenance, charging)
  * `reservedBy` (String or null): userId of the user who reserved the vehicle, or null if not reserved
  * `rentedBy` (String or null): userId of the user who rented the vehicle, or null if not rented
  * `currentStation` (String or null): stationId where the vehicle is currently parked, or null if not parked at a station