# ACMEMobility - Servizio Stazioni (Python / FastAPI)
# Porta 5000 : HTTP/REST
# Un contenitore = Una stazione
# Configurazione tramite variabili d'ambiente:
#   STATION_ID, STATION_NAME, STATION_LAT, STATION_LON, STATION_ADDRESS

import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from get_env import get_env_or_exit
from vehicle_status import VehicleStatus


app = FastAPI(title="ACMEMobility - Station Service")
logger = logging.getLogger(__name__)


# Configurazione della stazione tramite variabili d'ambiente
STATION_ID      = get_env_or_exit("STATION_ID")
STATION_PREFIX	= get_env_or_exit('STATION_PREFIX')

# Ottieni informazioni sulla stazione
STATION_SUFFIX	= STATION_ID.split(f'{STATION_PREFIX}-')[1] 
STATION_NUMBER  = STATION_SUFFIX.rsplit("-", 1)[-1]
STATION_NAME	= get_env_or_exit(f"STATION_{STATION_NUMBER}_NAME")
STATION_ADDRESS = get_env_or_exit(f"STATION_{STATION_NUMBER}_ADDRESS")
STATION_LAT     = float(get_env_or_exit(f"COORD_STATION_{STATION_NUMBER}_LAT"))
STATION_LON     = float(get_env_or_exit(f"COORD_STATION_{STATION_NUMBER}_LON"))

VEHICLE_N       = int(get_env_or_exit('VEHICLE_N'))
VEHICLE_PREFIX  = get_env_or_exit('VEHICLE_PREFIX')
ENV_VEHICLE_START_STATIONS = {}
for i in range(1, VEHICLE_N + 1):
	vehicle_suffix = str(i).zfill(2)
	ENV_VEHICLE_START_STATIONS[vehicle_suffix] = get_env_or_exit(f"VEHICLE_{vehicle_suffix}_START_STATION")


vehicles = {}
for vehicle_suffix, start_station in ENV_VEHICLE_START_STATIONS.items():
	if start_station == STATION_ID:
		vehicle_id = get_env_or_exit(f"VEHICLE_ID_{vehicle_suffix}")
		vehicles[vehicle_id] = {
			"id": vehicle_id,
			"status": VehicleStatus.LOCKED.name
		}

# Informazioni sulla stazione corrente
station = {
	"id": STATION_ID,
	"name": STATION_NAME,
	"address": STATION_ADDRESS,
	"lat": STATION_LAT,
	"lon": STATION_LON,
	"vehicles": vehicles
}

logger.info("[STATION] Starting station %s - %s", STATION_ID, STATION_NAME)


# Modelli delle richieste
class UnlockRequest(BaseModel):
	vehicleId: str  # ID del veicolo da sbloccare

class LockRequest(BaseModel):
	vehicleId: str                        # ID del veicolo da bloccare

class ParkRequest(BaseModel):
	vehicleId: str  # ID del veicolo da parcheggiare


# Controllo stato del servizio
@app.get("/health")
def health():
	return {"status": "running", "stationId": STATION_ID, "stationName": STATION_NAME}, 200

# Restituisce le informazioni della stazione e i suoi veicoli
@app.get("/station")
def get_station():
	return station, 200

# Sblocca un veicolo (inizio noleggio) - cambia stato in 'rented'
@app.post("/vehicle/unlock")
def unlock_vehicle(req: UnlockRequest):
	# Controlla se il veicolo esiste in questa stazione
	if req.vehicleId not in vehicles:
		logger.error("[STATION %s] Vehicle %s not found!", STATION_ID, req.vehicleId)
		return JSONResponse(status_code=404, content={
			"success": False,
			"message": f"Vehicle {req.vehicleId} not found at station {STATION_ID}"
		})

	vehicle = vehicles[req.vehicleId]

	# Controlla se il veicolo è disponibile o prenotato
	if vehicle["status"] != VehicleStatus.LOCKED.name:
		logger.error("[STATION %s] Vehicle %s is not available (status: %s)", STATION_ID, req.vehicleId, vehicle["status"])
		return JSONResponse(status_code=400, content={
			"success": False,
			"message": f"Vehicle {req.vehicleId} is not available (status: {vehicle['status']})"
		})

	# Sblocca il veicolo
	vehicles.pop(req.vehicleId)

	logger.info("[STATION %s] Unlocked vehicle %s", STATION_ID, req.vehicleId)

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
		logger.error("[STATION %s] Vehicle %s not found!", STATION_ID, req.vehicleId)
		return JSONResponse(status_code=404, content={
			"success": False,
			"message": f"Vehicle {req.vehicleId} not found at station {STATION_ID}"
		})

	vehicle = vehicles[req.vehicleId]

	# Controlla se il veicolo è attualmente noleggiato
	if vehicle["status"] != VehicleStatus.PARKED.name:
		logger.error("[STATION %s] Vehicle %s is not currently parked (status: %s)", STATION_ID, req.vehicleId, vehicle["status"])
		return JSONResponse(status_code=400, content={
			"success": False,
			"message": f"Vehicle {req.vehicleId} is not currently parked (status: {vehicle['status']})"
		})

	# Ripristina lo stato e aggiorna la batteria se fornita
	vehicle["status"] = VehicleStatus.LOCKED.name

	logger.info("[STATION %s] Locked vehicle %s", STATION_ID, req.vehicleId)

	return {
		"success": True,
		"vehicleId": req.vehicleId,
		"stationId": STATION_ID,
		"message": f"Vehicle {req.vehicleId} locked successfully at {STATION_NAME}"
	}


@app.post("/hardware/insert")
def park_vehicle(req: ParkRequest):
	# Controlla se il veicolo esiste in questa stazione
	if req.vehicleId in vehicles:
		logger.warning(
			"Vehicle %s is at station %s with status %s. Overwriting status.",
			req.vehicleId, STATION_ID, vehicles[req.vehicleId]["status"]
		)

	# Simula l'inserimento fisico nel dock
	vehicles[req.vehicleId] = {
		"id": req.vehicleId,
		"status": VehicleStatus.PARKED.name
	}

	logger.info("[STATION %s] Parked vehicle %s", STATION_ID, req.vehicleId)

	return {
		"success": True,
		"vehicleId": req.vehicleId,
		"message": f"Vehicle {req.vehicleId} successfully parked in the station dock."
	}


# Avvio del server
if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
