import logging
from flask import Flask, request, jsonify
from datetime import datetime

from db import DATABASE
from get_env import get_env_or_exit



app = Flask(__name__)
logger = logging.getLogger(__name__)


PORT_FLEET_BATTERY	= int(get_env_or_exit('PORT_FLEET_BATTERY'))


# Stockage en mémoire uniquement des batteries
batteries = {}

# POST /battery/update
@app.route('/battery/<vehicle_id>', methods=['POST'])
def update_battery(vehicle_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    battery = data.get("battery")

    if not vehicle_id or battery is None:
        return jsonify({"error": "vehicleId and battery are required"}), 400

    batteries[vehicle_id] = {
        "battery": battery,
        "timestamp": datetime.now().isoformat()
    }

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
    if vehicle_id not in batteries:
        return jsonify({"error": "Vehicle not found"}), 404

    logger.info("[%s] Battery requested: %s%%", vehicle_id, batteries[vehicle_id]["battery"])
    return jsonify({
        "vehicleId": vehicle_id,
        "battery": batteries[vehicle_id]["battery"],
        "timestamp": batteries[vehicle_id]["timestamp"]
    })


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=PORT_FLEET_BATTERY)