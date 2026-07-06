# Fleet Management API Reference

As per the architectural constraints, Fleet Management is a composite microservice consisting of a Tracking Service and a Battery/State Monitoring Service.

## Domain A: Tracking Service
Responsible for tracking the real-time geographical position and movement state of the vehicles.
*   **Base URL:** `http://<fleet-tracking-host>:<PORT_FLEET>`

### Start Tracking (`/tracking/start`)
Activates the GPS tracking loop for a specific vehicle when a ride begins.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "vehicleId": "V-123",
  "userId": "U-55"
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

### Stop Tracking (`/tracking/stop`)
Deactivates the GPS tracking loop for a specific vehicle when a ride ends.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
	"vehicleId": "V-123",
	"userId": "U-55"
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

### Get Vehicle Position (`/tracking/position/{vehicleId}`)
Fetch the vehicle's current location.

*   **Method:** `GET`
*   **URL Parameter:** `vehicleId` (e.g., `/tracking/position/V-123`)
*   **Response (200 OK):**
```json
{
  "vehicleId": "V-123",
  "coordinates": {
    "latitude": 44.4949,
    "longitude": 11.3426
  },
  "speedKmH": 22.5,
  "status": "MOVING"
}
```

### Get All vehicles positions (`/tracking/position`)
Fetch the current locations of all vehicles.

*   **Method:** `GET`
*   **Response (200 OK):**
```json
{
  "vehicles": [
    {
      "vehicleId": "V-123",
      "coordinates": {
        "latitude": 44.4949,
        "longitude": 11.3426
      },
      "speedKmH": 22.5,
      "status": "MOVING"
    },
    {
      "vehicleId": "V-456",
  "coordinates": {
        "latitude": 44.4949,
        "longitude": 11.3426
      },
      "speedKmH": 22.5,
      "status": "MOVING"
    }
  ]
}
```

### Upload Vehicle Position (`/tracking/position/{vehicleId}`)
Upload the vehicle's current location.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "coordinates": {
    "latitude": 44.4949,
    "longitude": 11.3426
  },
  "speedKmH": 22.5,
  "status": "MOVING",
  "timeEpochS": 1690000000.2
}
```
*   **Response (200 OK):**
```json
{
  "success": true,
  "message": "Position updated successfully."
}
```

---

## Domain B: Battery & State Service
Responsible for monitoring vehicle status, information and health (mostly battery level).
*   **Base URL:** `http://<fleet-battery-host>:4002`

### Fetch Battery Level (`/battery/{vehicleId}`)
Retrieves the current battery percentage of the vehicle.

*   **Method:** `GET`
*   **URL Parameter:** `vehicleId` (e.g., `/battery/V-123`)
*   **Response (200 OK):**
```json
{
  "vehicleId": "V-123",
  "batteryLevel": 12
}
```

### Update Battery Level (`/battery/{vehicleId}`)
Updates the battery level of a vehicle, typically called by the vehicle itself.  
*   **Method:** `POST`
*   **URL Parameter:** `vehicleId` (e.g., `/battery/V-123`)
*   **Request Body (JSON):**
```json
{
  "battery": 12,
  "timeEpochS": 1690000000.2
}
```
*   **Response (200 OK):**
```json
{
  "success": true,
  "message": "Battery level updated successfully."
}```
