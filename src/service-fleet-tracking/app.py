import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import requests

from db import DATABASE
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


# Memorizzazione in memoria
vehicles = {}

# currently tracked vehicles
tracked_vehicles = set()



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
		tracked_vehicles.add(vehicle_id)

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
		tracked_vehicles.discard(vehicle_id)

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

	# Verifica dei dati
	if not vehicle_id or lat is None or lon is None:
		return jsonify({"error": "vehicleId, x, y are required"}), 400

	position = {
		"latitude": lat,
		"longitude": lon,
		"timestamp": datetime.now().isoformat()
	}

	# Nuovo veicolo
	if vehicle_id not in vehicles:
		vehicles[vehicle_id] = {
			"current": position,
			"history": [position]
		}
	else:
		vehicles[vehicle_id]["current"] = position
		vehicles[vehicle_id]["history"].append(position)

		# Limitare la cronologia a 100 posizioni
		if len(vehicles[vehicle_id]["history"]) > 100:
			vehicles[vehicle_id]["history"].pop(0)

	logging.info("[%s] Position updated: latitude=%s, longitude=%s", vehicle_id, lat, lon)
	return jsonify({
		"status": "success",
		"message": "Position updated"
	}), 200


# GET /position/<vehicle_id>

@app.route('/position/<vehicle_id>', methods=['GET'])
def get_position(vehicle_id):
	if vehicle_id not in vehicles:
		return jsonify({"error": "Vehicle not found"}), 404

	logging.info("[%s] Position requested: latitude=%s, longitude=%s", vehicle_id, vehicles[vehicle_id]["current"]["latitude"], vehicles[vehicle_id]["current"]["longitude"])
	return jsonify({
		"vehicleId": vehicle_id,
		"current": vehicles[vehicle_id]["current"]
	})


# GET /position/active

@app.route('/position/active', methods=['GET'])
def get_active_vehicles():
	active_ids = list(vehicles.keys())

	return jsonify({
		"activeVehicles": active_ids
	})


# GET /position/<vehicle_id>/history

@app.route('/position/<vehicle_id>/history', methods=['GET'])
def get_history(vehicle_id):
	if vehicle_id not in vehicles:
		return jsonify({"error": "Vehicle not found"}), 404

	return jsonify({
		"vehicleId": vehicle_id,
		"history": vehicles[vehicle_id]["history"]
	})


# GET /position/all
# needed for leaflet/graphhopper
@app.route('/position/all', methods=['GET'])
def get_all_positions():
	last_positions = {vehicle_id: vehicles[vehicle_id]["current"] for vehicle_id in tracked_vehicles}
	return jsonify(last_positions), 200



if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=PORT_FLEET_TRACKING)