# ACMEMobility - Servizio Stazioni (Python / FastAPI)
# Porta 5000 : HTTP/REST
# Un contenitore = Una stazione
#
# Logica veicoli semplificata:
#   - La stazione conosce solo i veicoli fisicamente presenti
#   - Stati possibili: "parked" (parcheggiato) o "locked" (bloccato/in uso)
#   - Se il veicolo non c'è in memoria = non è presente nella stazione
#
# Endpoints:
#   POST /hardware/insert  -> aggiunge un veicolo alla stazione (parcheggio)
#   POST /vehicle/unlock   -> sblocca un veicolo (inizio noleggio, lo rimuove dalla stazione)
#   POST /vehicle/lock     -> blocca un veicolo (fine noleggio, lo aggiunge alla stazione)
#   GET  /station          -> info della stazione e veicoli presenti
#   GET  /health           -> controllo stato del servizio

import os
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="ACMEMobility - Station Service")

# Configurazione della stazione tramite variabili d'ambiente
STATION_ID      = os.environ.get("STATION_ID", "ST-01")
STATION_NAME    = os.environ.get("STATION_NAME", "Stazione Centrale")
STATION_ADDRESS = os.environ.get("STATION_ADDRESS", "Piazza delle Medaglie d'Oro, Bologna")
STATION_LAT     = float(os.environ.get("STATION_LAT", "44.5058"))
STATION_LON     = float(os.environ.get("STATION_LON", "11.3429"))

# Veicoli inizialmente parcheggiati in questa stazione
# Letti dalla variabile d'ambiente INITIAL_VEHICLES (es. "V-001,V-002")
# Se non specificati, la stazione parte vuota
initial_vehicles_env = os.environ.get("INITIAL_VEHICLES", "V-001,V-002")
initial_vehicles = [v.strip() for v in initial_vehicles_env.split(",") if v.strip()]

# Memoria della stazione: dizionario vehicleId -> stato ("parked" o "locked")
# Solo i veicoli fisicamente presenti nella stazione sono in memoria
vehicles = {v: "parked" for v in initial_vehicles}

print(f"[STATION] Avvio stazione {STATION_ID} - {STATION_NAME}")
print(f"[STATION] Veicoli iniziali: {list(vehicles.keys())}")

# Modelli delle richieste
class InsertRequest(BaseModel):
    vehicleId: str  # ID del veicolo che arriva alla stazione

class UnlockRequest(BaseModel):
    vehicleId: str  # ID del veicolo da sbloccare (inizio noleggio)

class LockRequest(BaseModel):
    vehicleId: str  # ID del veicolo da bloccare (fine noleggio)

# Controllo stato del servizio
@app.get("/health")
def health():
    return {
        "status": "running",
        "stationId": STATION_ID,
        "stationName": STATION_NAME
    }

# Restituisce le info della stazione e i veicoli presenti
@app.get("/station")
def get_station():
    return {
        "id": STATION_ID,
        "name": STATION_NAME,
        "address": STATION_ADDRESS,
        "lat": STATION_LAT,
        "lon": STATION_LON,
        "vehicles": vehicles  # solo i veicoli presenti fisicamente
    }

# Aggiunge un veicolo alla stazione (parcheggio fisico)
@app.post("/hardware/insert")
def insert_vehicle(req: InsertRequest):
    # Aggiunge il veicolo con stato "parked"
    vehicles[req.vehicleId] = "parked"

    print(f"[STATION {STATION_ID}] INSERITO veicolo {req.vehicleId}")

    return {
        "success": True,
        "vehicleId": req.vehicleId,
        "stationId": STATION_ID,
        "status": "parked",
        "message": f"Vehicle {req.vehicleId} inserted at station {STATION_NAME}"
    }

# Sblocca un veicolo (inizio noleggio) - lo rimuove dalla memoria della stazione
@app.post("/vehicle/unlock")
def unlock_vehicle(req: UnlockRequest):
    # Controlla se il veicolo è presente nella stazione
    if req.vehicleId not in vehicles:
        return {
            "success": False,
            "vehicleId": req.vehicleId,
            "stationId": STATION_ID,
            "message": f"Vehicle {req.vehicleId} not found at station {STATION_ID}"
        }

    # Controlla se il veicolo è parcheggiato (non già bloccato)
    if vehicles[req.vehicleId] != "parked":
        return {
            "success": False,
            "vehicleId": req.vehicleId,
            "stationId": STATION_ID,
            "message": f"Vehicle {req.vehicleId} is not parked (status: {vehicles[req.vehicleId]})"
        }

    # Rimuove il veicolo dalla stazione (è in uso)
    del vehicles[req.vehicleId]

    print(f"[STATION {STATION_ID}] SBLOCCATO veicolo {req.vehicleId} - rimosso dalla stazione")

    return {
        "success": True,
        "vehicleId": req.vehicleId,
        "stationId": STATION_ID,
        "message": f"Vehicle {req.vehicleId} unlocked and removed from station {STATION_NAME}"
    }

# Blocca un veicolo (fine noleggio) - lo aggiunge alla stazione con stato "locked"
@app.post("/vehicle/lock")
def lock_vehicle(req: LockRequest):
    # Controlla se il veicolo è già presente nella stazione
    if req.vehicleId in vehicles:
        return {
            "success": False,
            "vehicleId": req.vehicleId,
            "stationId": STATION_ID,
            "message": f"Vehicle {req.vehicleId} already present at station {STATION_ID}"
        }

    # Aggiunge il veicolo con stato "locked"
    vehicles[req.vehicleId] = "locked"

    print(f"[STATION {STATION_ID}] BLOCCATO veicolo {req.vehicleId} - aggiunto alla stazione")

    return {
        "success": True,
        "vehicleId": req.vehicleId,
        "stationId": STATION_ID,
        "message": f"Vehicle {req.vehicleId} locked at station {STATION_NAME}"
    }

# Avvio del server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
