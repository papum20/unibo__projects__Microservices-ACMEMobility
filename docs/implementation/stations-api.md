# Stations Service API Reference

This service handles the physical interaction with the stations scattered around the city, specifically sending signals to the hardware to physically lock and unlock the vehicles.

*   **Base URL:** `http://<stations-service-host>:<PORT_STATIONS>`
*   **Protocol:** REST / JSON

## Unlock Vehicle (`/vehicle/unlock`)
Sends a physical command to the station's hardware to release the vehicle from the dock.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "vehicleId": "V-123"
}
```
*   **Response (200 OK):**
```json
{
  "success": true,
  "vehicleId": "V-123",
  "message": "Vehicle successfully released from the dock."
}
```

## Lock Vehicle (`/vehicle/lock`)
Sends a physical command to the station's hardware to lock the vehicle back into the dock at the end of a ride.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "vehicleId": "V-123"
}
```
*   **Response (200 OK):**
```json
{
  "success": true,
  "vehicleId": "V-123",
  "message": "Vehicle successfully secured in the dock."
}
```

## Park Vehicle (`/hardware/insert`)
Simulate the action of parking a vehicle, i.e. inserting it into a station dock. The station will automatically detect the vehicle in the correct dock, so it can then lock it upon request.  

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "vehicleId": "V-123"
}
```
*   **Response (200 OK):**
```json
{
  "success": true,
  "vehicleId": "V-123",
  "message": "Vehicle successfully parked in the station dock."
}
```

## Additional info

### Health (`/health`)

*   **Method:** `GET`
*   **Response (200 OK):**
```json
{
  "status": "running",
  "stationId": "ST-01",
  "stationName": "Stazione Centrale"
}
```

### Station info (`/station`)

*   **Method:** `GET`
*   **Response (200 OK):**
```json
{
  "stationId": "ST-01",
  "stationName": "Stazione Centrale",
  "stationAddress": "Piazza delle Medaglie d'Oro, Bologna",
  "latitude": 44.5058,
  "longitude": 11.3429,
  "vehicles": [
    {
      "vehicleId": "V-123",
      "status": "available"
    },
    {
      "vehicleId": "V-124",
      "status": "available"
    }
  ]
}
```
