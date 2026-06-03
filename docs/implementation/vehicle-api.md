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

## Simulation

### Set route start (`/simulate/end`)
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
