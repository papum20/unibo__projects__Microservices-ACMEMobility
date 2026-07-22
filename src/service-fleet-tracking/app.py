import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# Memorizzazione in memoria
from db import DATABASE, HistoryEntry
from get_env import get_env_or_exit
from util import get_vehicle_url



app = Flask(__name__)
CORS(app)	# allows the browser to fetch data from this API
logger = logging.getLogger(__name__)


UPDATE_TIMER_S	= 5

VEHICLE_PREFIX      = get_env_or_exit('VEHICLE_PREFIX')
URL_VEHICLE_PARAM   = get_env_or_exit('URL_VEHICLE_PARAM')
PORT_FLEET_TRACKING	= int(get_env_or_exit('PORT_FLEET_TRACKING'))

EP_VEHICLE_START    = get_env_or_exit('ENDPOINT_VEHICLE_TRACK_START')
EP_VEHICLE_STOP     = get_env_or_exit('ENDPOINT_VEHICLE_TRACK_STOP')



# POST /tracking/start

@app.route('/start', methods=['POST'])
def start_tracking():
	vehicle_id = request.json.get("vehicleId")
	
	if not vehicle_id:
		return jsonify({"error": "missing vehicleId"}), 400

	# notify vehicle itself
	vehicle_url = f"{get_vehicle_url(vehicle_id)}{EP_VEHICLE_START}"
	try:
		response = requests.post(vehicle_url, timeout=UPDATE_TIMER_S)
		response.raise_for_status()

		DATABASE.set_vehicle_tracking(vehicle_id, True)
		logger.info("[%s] Tracking STARTED.", vehicle_id)
		return jsonify({"success": True, "message": f"Tracking started for {vehicle_id}"}), 200
	except requests.exceptions.RequestException as e:
		logger.error("Failed to start vehicle %s: %s", vehicle_id, e)
		return jsonify({"success": False, "message": f"Vehicle offline or error: {e}"}), 503


# POST /tracking/stop

@app.route('/stop', methods=['POST'])
def stop_tracking():
	vehicle_id = request.json.get("vehicleId")
	
	if not vehicle_id:
		return jsonify({"error": "missing vehicleId"}), 400

	vehicle_url = f"{get_vehicle_url(vehicle_id)}{EP_VEHICLE_STOP}"
	try:
		response = requests.post(vehicle_url, timeout=UPDATE_TIMER_S)
		response.raise_for_status()
		DATABASE.set_vehicle_tracking(vehicle_id, False)

		logger.info("[%s] Tracking STOPPED.", vehicle_id)
		return jsonify({"success": True, "message": f"Tracking stopped for {vehicle_id}"}), 200
	except requests.exceptions.RequestException as e:
		logger.error("Failed to stop vehicle %s: %s", vehicle_id, e)
		return jsonify({"success": False, "message": f"Vehicle offline or error: {e}"}), 503


# POST /position/update

@app.route('/position/<vehicle_id>', methods=['POST'])
def update_position(vehicle_id):
	data = request.get_json()

	if not data:
		return jsonify({"error": "Invalid JSON"}), 400

	coordinates = data.get("coordinates")
	lat = coordinates.get("latitude") if coordinates else ""
	lon = coordinates.get("longitude") if coordinates else ""
	speedKmH = data.get("speedKmH")
	status = data.get("status")
	timeEpochS = data.get("timeEpochS")

	# Verifica dei dati
	if not vehicle_id or lat is None or lon is None or speedKmH is None or status is None or timeEpochS is None:
		return jsonify({"error": "vehicleId, x, y are required"}), 400

	lat, lon = float(lat), float(lon)
	history_entry = HistoryEntry(
		latitude		= lat,
		longitude		= lon,
		speed_kmh		= speedKmH,
		status			= status,
		time_epoch_s	= timeEpochS
	)

	vehicle = DATABASE.get_vehicle(vehicle_id)

	# Nuovo veicolo
	if vehicle is None:
		vehicle = DATABASE.add_vehicle(vehicle_id)
	DATABASE.add_vehicle_position(vehicle_id, history_entry)

	logging.info("[%s] Position updated: latitude=%s, longitude=%s", vehicle_id, lat, lon)
	return jsonify({
		"status": "success",
		"message": "Position updated"
	}), 200


# GET /position/<vehicle_id>

@app.route('/position/<vehicle_id>', methods=['GET'])
def get_position(vehicle_id):
	vehicle = DATABASE.get_vehicle(vehicle_id)
	if vehicle is None:
		return jsonify({"error": "Vehicle not found"}), 404

	current_position = vehicle.current
	if current_position is None:
		return jsonify({"error": "No position data available for this vehicle"}), 404

	logging.info("[%s] Position requested: %s", vehicle_id, str(current_position.to_dict()))
	return jsonify({
		"vehicleId": vehicle_id,
		"coordinates": {
			"latitude": current_position.latitude,
			"longitude": current_position.longitude
		},
		"speedKmH": current_position.speed_kmh,
		"status": current_position.status,
		"timeEpochS": current_position.time_epoch_s
	})


# GET /position/<vehicle_id>/history

@app.route('/position/<vehicle_id>/history', methods=['GET'])
def get_history(vehicle_id):
	vehicle = DATABASE.get_vehicle(vehicle_id)
	if vehicle is None:
		return jsonify({"error": "Vehicle not found"}), 404

	return jsonify({
		"vehicleId": vehicle_id,
		"history": [entry.to_dict() for entry in vehicle.history]
	})


# GET /position/active

@app.route('/position/active', methods=['GET'])
def get_active_vehicles():
	vehicles = DATABASE.get_all_vehicles()
	active_vehicles = [v for v in vehicles if v.is_tracked]

	return jsonify({
		"activeVehicles": [{
				"vehicleId": v.vehicle_id,
				"currentPosition": v.current.to_dict() if v.current else None
			}
			for v in active_vehicles
		]
	}), 200


# GET /position/all
# needed for leaflet/graphhopper
@app.route('/position/all', methods=['GET'])
def get_all_positions():
	all_positions = {}
	
	# Loop through all vehicles and grab the latest position if they are actively tracked
	for vehicle in DATABASE.get_all_vehicles():
		if vehicle.is_tracked and vehicle.current:
			all_positions[vehicle.vehicle_id] = vehicle.current.to_dict()
			
	return jsonify(all_positions), 200



if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=PORT_FLEET_TRACKING)