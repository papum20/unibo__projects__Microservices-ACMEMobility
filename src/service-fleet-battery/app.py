from flask import Flask, request, jsonify
from datetime import datetime

from db import DATABASE



app = Flask(__name__)

# Stockage en mémoire uniquement des batteries
batteries = {}

# 1. POST /battery/update
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

    return jsonify({
        "status": "success",
        "message": "Battery updated",
        "batteryWarning": warning
    }), 200


# 2. GET /battery/<vehicle_id>
@app.route('/battery/<vehicle_id>', methods=['GET'])
def get_battery(vehicle_id):
    if vehicle_id not in batteries:
        return jsonify({"error": "Vehicle not found"}), 404

    return jsonify({
        "vehicleId": vehicle_id,
        "battery": batteries[vehicle_id]["battery"],
        "timestamp": batteries[vehicle_id]["timestamp"]
    })


if __name__ == "__main__":
    app.run(debug=True, port=5002)