# ACMEMobility - Servizio Stazioni (Python / FastAPI)
# Porta 5000 : HTTP/REST
# Un contenitore = Una stazione
# Configurazione tramite variabili d'ambiente:
#   STATION_ID, STATION_NAME, STATION_LAT, STATION_LON, STATION_ADDRESS

import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="ACMEMobility - Station Service")

# Configurazione della stazione tramite variabili d'ambiente
STATION_ID      = os.environ.get("STATION_ID", "ST-01")
STATION_NAME    = os.environ.get("STATION_NAME", "Stazione Centrale")
STATION_ADDRESS = os.environ.get("STATION_ADDRESS", "Piazza delle Medaglie d'Oro, Bologna")
STATION_LAT     = float(os.environ.get("STATION_LAT", "44.5058"))
STATION_LON     = float(os.environ.get("STATION_LON", "11.3429"))

# Veicoli in memoria per questa stazione
# Possono essere configurati tramite VEHICLES_JSON oppure si usano 2 veicoli di default
default_vehicles = {
    "V-001": {"id": "V-001", "type": "scooter", "status": "available", "battery": 85},
    "V-002": {"id": "V-002", "type": "auto",    "status": "available", "battery": 92},
}

vehicles_json = os.environ.get("VEHICLES_JSON", None)
if vehicles_json:
    vehicles = json.loads(vehicles_json)
else:
    vehicles = default_vehicles

# Informazioni sulla stazione corrente
station = {
    "id": STATION_ID,
    "name": STATION_NAME,
    "address": STATION_ADDRESS,
    "lat": STATION_LAT,
    "lon": STATION_LON,
    "vehicles": vehicles
}

print(f"[STATION] Avvio stazione {STATION_ID} - {STATION_NAME}")

# Modelli delle richieste
class UnlockRequest(BaseModel):
    vehicleId: str  # ID del veicolo da sbloccare

class LockRequest(BaseModel):
    vehicleId: str                        # ID del veicolo da bloccare
    batteryLevel: Optional[float] = None  # Livello batteria alla riconsegna (opzionale)

# Controllo stato del servizio
@app.get("/health")
def health():
    return {"status": "running", "stationId": STATION_ID, "stationName": STATION_NAME}

# Restituisce le informazioni della stazione e i suoi veicoli
@app.get("/station")
def get_station():
    return station

# Sblocca un veicolo (inizio noleggio) - cambia stato in 'rented'
@app.post("/vehicle/unlock")
def unlock_vehicle(req: UnlockRequest):
    # Controlla se il veicolo esiste in questa stazione
    if req.vehicleId not in vehicles:
        return {
            "success": False,
            "message": f"Vehicle {req.vehicleId} not found at station {STATION_ID}"
        }

    vehicle = vehicles[req.vehicleId]

    # Controlla se il veicolo è disponibile o prenotato
    if vehicle["status"] not in ["available", "booked"]:
        return {
            "success": False,
            "message": f"Vehicle {req.vehicleId} is not available (status: {vehicle['status']})"
        }

    # Sblocca il veicolo
    vehicle["status"] = "rented"

    print(f"[STATION {STATION_ID}] SBLOCCATO veicolo {req.vehicleId}")

    return {
        "success": True,
        "vehicleId": req.vehicleId,
        "stationId": STATION_ID,
        "message": f"Vehicle {req.vehicleId} unlocked successfully at {STATION_NAME}"
    }

# Blocca un veicolo (fine noleggio / riconsegna) - cambia stato in 'available'
@app.post("/vehicle/lock")
def lock_vehicle(req: LockRequest):
    # Controlla se il veicolo esiste in questa stazione
    if req.vehicleId not in vehicles:
        return {
            "success": False,
            "message": f"Vehicle {req.vehicleId} not found at station {STATION_ID}"
        }

    vehicle = vehicles[req.vehicleId]

    # Controlla se il veicolo è attualmente noleggiato
    if vehicle["status"] != "rented":
        return {
            "success": False,
            "message": f"Vehicle {req.vehicleId} is not currently rented (status: {vehicle['status']})"
        }

    # Ripristina lo stato e aggiorna la batteria se fornita
    vehicle["status"] = "available"
    if req.batteryLevel is not None:
        vehicle["battery"] = req.batteryLevel

    print(f"[STATION {STATION_ID}] BLOCCATO veicolo {req.vehicleId} (batteria: {vehicle['battery']}%)")

    return {
        "success": True,
        "vehicleId": req.vehicleId,
        "stationId": STATION_ID,
        "batteryLevel": vehicle["battery"],
        "lowBattery": vehicle["battery"] < 15,  # True se batteria sotto 15% -> penale 10%
        "message": f"Vehicle {req.vehicleId} locked successfully at {STATION_NAME}"
    }

# Avvio del server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
