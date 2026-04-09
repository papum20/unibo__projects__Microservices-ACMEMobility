# ============================================================
# ACMEMobility - Station Service (Python / FastAPI)
# PORT 5000 : HTTP/REST
#
# Operations:
#   POST /vehicle/unlock -> unlocks a vehicle at a station
#   POST /vehicle/lock   -> locks a vehicle at a station
#   GET  /stations       -> returns all stations and their vehicles
#   GET  /stations/{id}  -> returns a specific station
# ============================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="ACMEMobility - Station Service")

# ============================================================
# Simulated stations (5 stations in Bologna)
# Vehicle status: "available", "booked", "rented", "maintenance"
# ============================================================
stations = {
    "ST-01": {
        "id": "ST-01",
        "name": "Stazione Centrale",
        "address": "Piazza delle Medaglie d'Oro, Bologna",
        "lat": 44.5058,
        "lon": 11.3429,
        "vehicles": {
            "V-001": {"id": "V-001", "type": "scooter", "status": "available", "battery": 85},
            "V-002": {"id": "V-002", "type": "auto",    "status": "available", "battery": 92},
        }
    },
    "ST-02": {
        "id": "ST-02",
        "name": "Piazza Maggiore",
        "address": "Piazza Maggiore, Bologna",
        "lat": 44.4938,
        "lon": 11.3430,
        "vehicles": {
            "V-003": {"id": "V-003", "type": "monopattino", "status": "available", "battery": 70},
            "V-004": {"id": "V-004", "type": "scooter",     "status": "available", "battery": 60},
        }
    },
    "ST-03": {
        "id": "ST-03",
        "name": "Università",
        "address": "Via Zamboni, Bologna",
        "lat": 44.4973,
        "lon": 11.3535,
        "vehicles": {
            "V-005": {"id": "V-005", "type": "auto",        "status": "available", "battery": 95},
            "V-006": {"id": "V-006", "type": "monopattino", "status": "available", "battery": 45},
        }
    },
    "ST-04": {
        "id": "ST-04",
        "name": "Fiera",
        "address": "Piazza Costituzione, Bologna",
        "lat": 44.5091,
        "lon": 11.3680,
        "vehicles": {
            "V-007": {"id": "V-007", "type": "scooter", "status": "available", "battery": 80},
            "V-008": {"id": "V-008", "type": "auto",    "status": "available", "battery": 55},
        }
    },
    "ST-05": {
        "id": "ST-05",
        "name": "Aeroporto",
        "address": "Via del Triumvirato, Bologna",
        "lat": 44.5354,
        "lon": 11.2887,
        "vehicles": {
            "V-009": {"id": "V-009", "type": "auto",        "status": "available", "battery": 100},
            "V-010": {"id": "V-010", "type": "monopattino", "status": "available", "battery": 30},
        }
    }
}

# ============================================================
# Request models
# ============================================================
class UnlockRequest(BaseModel):
    stationId: str
    vehicleId: str

class LockRequest(BaseModel):
    stationId: str
    vehicleId: str
    batteryLevel: Optional[float] = None

# ============================================================
# Helper: find vehicle across all stations
# ============================================================
def find_vehicle(station_id: str, vehicle_id: str):
    if station_id not in stations:
        return None, None
    station = stations[station_id]
    if vehicle_id not in station["vehicles"]:
        return None, None
    return station, station["vehicles"][vehicle_id]

# ============================================================
# Routes
# ============================================================

@app.get("/")
def root():
    return {"service": "ACMEMobility Station Service", "status": "running", "port": 5000}

@app.get("/stations")
def get_stations():
    """Returns all stations with their vehicles"""
    return {"stations": list(stations.values())}

@app.get("/stations/{station_id}")
def get_station(station_id: str):
    """Returns a specific station"""
    if station_id not in stations:
        raise HTTPException(status_code=404, detail=f"Station {station_id} not found")
    return stations[station_id]

@app.post("/vehicle/unlock")
def unlock_vehicle(req: UnlockRequest):
    """
    Unlocks a vehicle at a station (start of rental).
    Sets vehicle status to 'rented'.
    """
    station, vehicle = find_vehicle(req.stationId, req.vehicleId)

    if not station or not vehicle:
        return {
            "success": False,
            "message": f"Vehicle {req.vehicleId} not found at station {req.stationId}"
        }

    if vehicle["status"] not in ["available", "booked"]:
        return {
            "success": False,
            "message": f"Vehicle {req.vehicleId} is not available (status: {vehicle['status']})"
        }

    # Unlock the vehicle
    vehicle["status"] = "rented"

    print(f"[STATION] UNLOCKED vehicle {req.vehicleId} at station {req.stationId}")

    return {
        "success": True,
        "vehicleId": req.vehicleId,
        "stationId": req.stationId,
        "message": f"Vehicle {req.vehicleId} unlocked successfully at {station['name']}"
    }

@app.post("/vehicle/lock")
def lock_vehicle(req: LockRequest):
    """
    Locks a vehicle at a station (end of rental / return).
    Sets vehicle status back to 'available'.
    Optionally updates battery level.
    """
    station, vehicle = find_vehicle(req.stationId, req.vehicleId)

    if not station or not vehicle:
        return {
            "success": False,
            "message": f"Vehicle {req.vehicleId} not found at station {req.stationId}"
        }

    if vehicle["status"] != "rented":
        return {
            "success": False,
            "message": f"Vehicle {req.vehicleId} is not currently rented (status: {vehicle['status']})"
        }

    # Lock the vehicle and update battery if provided
    vehicle["status"] = "available"
    if req.batteryLevel is not None:
        vehicle["battery"] = req.batteryLevel

    print(f"[STATION] LOCKED vehicle {req.vehicleId} at station {req.stationId} (battery: {vehicle['battery']}%)")

    return {
        "success": True,
        "vehicleId": req.vehicleId,
        "stationId": req.stationId,
        "batteryLevel": vehicle["battery"],
        "lowBattery": vehicle["battery"] < 15,
        "message": f"Vehicle {req.vehicleId} locked successfully at {station['name']}"
    }

# ============================================================
# Run
# ============================================================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
