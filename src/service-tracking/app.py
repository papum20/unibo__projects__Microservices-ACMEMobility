from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Memorizzazione in memoria
vehicles = {}

# 1. POST /positions/update

@app.route('/positions/update', methods=['POST'])
def update_position():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON non valido"}), 400

    vehicle_id = data.get("vehicleId")
    x = data.get("x")
    y = data.get("y")

    # Verifica dei dati
    if not vehicle_id or x is None or y is None:
        return jsonify({"error": "vehicleId, x, y sono obbligatori"}), 400

    position = {
        "x": x,
        "y": y,
        "timestamp": datetime.utcnow().isoformat()
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


# 2. GET /positions/<vehicle_id>
@app.route('/positions/<vehicle_id>', methods=['GET'])
def get_position(vehicle_id):
    if vehicle_id not in vehicles:
        return jsonify({"error": "Veicolo non trovato"}), 404

    return jsonify({
        "vehicleId": vehicle_id,
        "current": vehicles[vehicle_id]["current"]
    })


# 3. GET /positions/active

@app.route('/positions/active', methods=['GET'])
def get_active_vehicles():
    active_ids = list(vehicles.keys())

    return jsonify({
        "activeVehicles": active_ids
    })


# 4. GET /positions/<vehicle_id>/history
@app.route('/positions/<vehicle_id>/history', methods=['GET'])
def get_history(vehicle_id):
    if vehicle_id not in vehicles:
        return jsonify({"error": "Veicolo non trovato"}), 404

    return jsonify({
        "vehicleId": vehicle_id,
        "history": vehicles[vehicle_id]["history"]
    })


if __name__ == "__main__":
    app.run(debug=True)