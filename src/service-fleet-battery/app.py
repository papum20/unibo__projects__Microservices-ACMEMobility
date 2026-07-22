import logging
from flask import Flask, request, jsonify
from datetime import datetime, timezone

# Stockage en mémoire uniquement des batteries
from db import DATABASE
from get_env import get_env_or_exit



app = Flask(__name__)
logger = logging.getLogger(__name__)


PORT_FLEET_BATTERY	= int(get_env_or_exit('PORT_FLEET_BATTERY'))



# POST /battery/update
@app.route('/battery/<vehicle_id>', methods=['POST'])
def update_battery(vehicle_id):
	data = request.get_json()

	if not data:
		return jsonify({"error": "Invalid JSON"}), 400

	battery = data.get("battery")

	if not vehicle_id or battery is None:
		return jsonify({"error": "vehicleId and battery are required"}), 400

	vehicle = DATABASE.get_vehicle(vehicle_id)
	if vehicle is None:
			vehicle = DATABASE.add_vehicle(vehicle_id)

	vehicle.battery_perc = battery
	vehicle.time_epoch_s = datetime.now(timezone.utc).timestamp()
	DATABASE.update_vehicle(vehicle)

	warning = None
	if battery < 15:
		warning = "Low battery"

	logger.info("[%s] Battery updated: %s%%", vehicle_id, battery)
	return jsonify({
		"status": "success",
		"message": "Battery updated",
		"batteryWarning": warning
	}), 200


# GET /battery/<vehicle_id>
@app.route('/battery/<vehicle_id>', methods=['GET'])
def get_battery(vehicle_id):
	vehicle = DATABASE.get_vehicle(vehicle_id)
	if not vehicle:
		return jsonify({"error": "Vehicle not found"}), 404

	logger.info("[%s] Battery requested: %s%%", vehicle_id, vehicle.battery_perc)
	return jsonify({
		"vehicleId": vehicle_id,
		"battery": vehicle.battery_perc,
		"timestamp": vehicle.time_epoch_s
	})


# GET /battery/all
@app.route('/battery/all', methods=['GET'])
def get_all_batteries():
	vehicles = DATABASE.get_all_vehicles()
	batteries = [vehicle.to_dict() for vehicle in vehicles]

	logger.info("All batteries requested: %s vehicles", len(batteries))
	return jsonify({
		"vehicles": batteries
	}), 200


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=PORT_FLEET_BATTERY)