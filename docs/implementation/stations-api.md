# Stations Service API Reference

This service handles the physical interaction with the stations scattered around the city, specifically sending signals to the hardware to physically lock and unlock the vehicles.

*   **Base URL:** `http://<stations-service-host>:<PORT_STATIONS>`
*   **Protocol:** REST / JSON

## 1. Unlock Vehicle (`/vehicle/unlock`)
Sends a physical command to the station's hardware to release the vehicle from the dock.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "vehicleId": "V-123",
  "stationId": "STATION-BOLOGNA-01" 
}
```
*   **Response (200 OK):**
```json
{
  "success": true,
  "vehicleId": "V-123",
  "status": "UNLOCKED",
  "message": "Vehicle successfully released from the dock."
}
```

## 2. Lock Vehicle (`/vehicle/lock`)
Sends a physical command to the station's hardware to lock the vehicle back into the dock at the end of a ride.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "vehicleId": "V-123",
  "stationId": "STATION-BOLOGNA-02"
}
```
*   **Response (200 OK):**
```json
{
  "success": true,
  "vehicleId": "V-123",
  "status": "LOCKED",
  "message": "Vehicle successfully secured in the dock."
}
```
