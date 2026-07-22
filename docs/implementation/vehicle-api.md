# Vehicle API Reference

Single vehicle API.  

## Start Tracking (`/tracking/start`)
Start the vehicle's sharing of position and other information.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
}
```
*   **Response (200 OK):**
```json
{
  "success": true,
  "trackingActive": true,
  "message": "Real-time tracking initiated."
}
```

## Stop Tracking (`/tracking/stop`)
Stop the vehicle's sharing of position and other information.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
}
```
*   **Response (200 OK):**
```json
{
	"success": true,
	"trackingActive": false,
	"message": "Real-time tracking stopped."
}
```

## Get Vehicle Information (`/status`)
Get the vehicle's current status, including position, battery level, and other relevant information.

*   **Method:** `GET`
*   **Response (200 OK):**
```json
{
  "vehicleId": "V-123",
  "coordinates": {
    "latitude": 44.4949,
    "longitude": 11.3426
  },
  "batteryLevel": 75,
  "speedKmH": 22.5,
  "status": "MOVING",
  "timeEpochS": 1697040000,
  "isTracking": true,
  "routeEnd": {
    "latitude": 44.4965,
    "longitude": 11.3410
  }
}
```

## Simulation

### Set route parking station (`/simulate/station`)
Set current station (e.g. when parking at a station).

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "stationId": "STATION-1"
}```
*   **Response (200 OK):**
```json
{
  "success": true,
  "message": "Current station set to STATION-1."
}
```

### Set route end (`/simulate/end`)
Set route end station (the start is where it is now).  

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "coordinates": {
    "latitude": 44.4965,
    "longitude": 11.3410
  }
}
```
*   **Response (200 OK):**
```json
{
  "success": true,
  "message": "Route end set to (44.4965, 11.3410)."
}
```

### Force move (`/simulate/force_move`)
Simulate the vehicle starting to move without ACME's knowledge (e.g., theft or unauthorized use).  

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
}
```
*   **Response (200 OK):**
```json
{
  "success": true,
  "message": "Vehicle moved without ACME's knowledge."
}
```
