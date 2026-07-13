# DataBases

## ACME DB

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
  * `batteryPerc` (Integer or null): last value fetched for battery level percentage (0-100)

## FleetManagement Tracking DB

* `Vehicles`:
  * `vehicleId` (String): Unique identifier for each vehicle
  * `isTracked` (Boolean): whether the vehicle is currently being tracked by ACME
  * `history` (List of {latitude: Float, longitude: Float, speedKmH: Float, status: String, timeEpochS: Float}): history of the vehicle's positions

## FleetManagement Battery DB

* `Vehicles`:
  * `vehicleId` (String): Unique identifier for each vehicle
  * `batteryPerc` (Integer): current battery level percentage (0-100)
  * `timeEpochS` (Float): timestamp of the last battery level update
