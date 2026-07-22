# ACME Mobility Service API Reference

The ACME Mobility service exposes its capabilities via the Camunda BPMN engine. The mobile app interacts with the system by sending messages to the Camunda REST API to trigger or progress rental workflows.

*   **Base URL:** `<URL_CAMUNDA_MESSAGE>`
*   **Protocol:** REST / JSON

## Start Immediate Rental (`acme_start_immediate`)
Triggered when a user scans a QR code on a vehicle without a prior reservation.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "messageName": "acme_start_immediate",
  "businessKey": "V-123",
  "processVariables": {
    "vehicleId": {"value": "V-123", "type": "String"},
    "userId": {"value": "USER-001", "type": "String"},
    "isImmediate": {"value": true, "type": "Boolean"}
  }
}
```

## Reserve Vehicle (`acme_start_reserve`)
Triggered when a user selects a vehicle on the map to reserve it for up to 30 minutes.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "messageName": "acme_start_reserve",
  "businessKey": "V-123",
  "processVariables": {
    "vehicleId": {"value": "V-123", "type": "String"},
    "userId": {"value": "USER-001", "type": "String"},
    "isImmediate": {"value": false, "type": "Boolean"}
  }
}
```

## Cancel Reservation (`user_cancel_reservation`)
Triggered when a user cancels an active reservation via the app.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "messageName": "user_cancel_reservation",
  "businessKey": "V-123"
}
```

## Scan Reserved Vehicle (`user_reserve_scan`)
Triggered when a user arrives at the vehicle they previously reserved and scans the QR code to start the ride.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "messageName": "user_reserve_scan",
  "businessKey": "V-123"
}
```

## Lock Vehicle & End Ride (`user_vehicle_locked`)
Triggered after the user has parked the vehicle at a station. This signal informs ACME that the physical lock has been engaged and the rental can be finalized.

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "messageName": "user_vehicle_locked",
  "businessKey": "V-123",
  "processVariables": {
    "stationId": {"value": "STATION-BOLOGNA-01", "type": "String"}
  }
}
```

## Assistance Lock (`user_assistance_lock`)
Emergency signal sent if the user cannot physically lock the vehicle at a station and requires backend intervention to secure the vehicle and stop billing.  
Note: `needsAssistance` is needed for implementation purposes (as a process variable in Camunda).  

*   **Method:** `POST`
*   **Request Body (JSON):**
```json
{
  "messageName": "user_assistance_lock",
  "businessKey": "V-123",
  "needsAssistance": true
}
```
