from flask import Flask, request, jsonify
from datetime import datetime
import requests



app = Flask(__name__)

# Memorizzazione in memoria
vehicles = {}

# currently tracked vehicles
tracked_vehicles = set()



# POST /tracking/start

@app.route('/tracking/start', methods=['POST'])
def start_tracking():
    vehicle_id = request.json.get("vehicleId")
    tracked_vehicles.add(vehicle_id)
    
    # notify vehicle itself
    vehicle_url = f"http://vehicle-{vehicle_id}:6000/start"
    try:
        requests.post(vehicle_url, timeout=5)
        return jsonify({"success": True}), 200
    except requests.exceptions.RequestException:
        return jsonify({"success": False, "message": "Vehicle offline"}), 503


# POST /position/update

@app.route('/position/<vehicle_id>', methods=['POST'])
def update_position(vehicle_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON non valido"}), 400

    x = data.get("x")
    y = data.get("y")

    # Verifica dei dati
    if not vehicle_id or x is None or y is None:
        return jsonify({"error": "vehicleId, x, y sono obbligatori"}), 400

    position = {
        "x": x,
        "y": y,
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

    return jsonify({
        "status": "successo",
        "message": "Posizione aggiornata"
    }), 200


# GET /position/<vehicle_id>

@app.route('/position/<vehicle_id>', methods=['GET'])
def get_position(vehicle_id):
    if vehicle_id not in vehicles:
        return jsonify({"error": "Veicolo non trovato"}), 404

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
        return jsonify({"error": "Veicolo non trovato"}), 404

    return jsonify({
        "vehicleId": vehicle_id,
        "history": vehicles[vehicle_id]["history"]
    })



if __name__ == "__main__":
    app.run(debug=True)