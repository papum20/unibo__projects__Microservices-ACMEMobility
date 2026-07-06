from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# =========================
# REGISTRO VEICOLI
# =========================

VEHICLES = {
    "V1": "http://localhost:5001",
    "V2": "http://localhost:5002",
    "V3": "http://localhost:5003"
}

# =========================
# AVVIO TRACCIAMENTO
# =========================

@app.route("/tracking/start", methods=["POST"])
def tracking_start():

    data = request.get_json()

    if not data or "vehicleId" not in data:
        return jsonify({"error": "vehicleId mancante"}), 400

    vehicle_id = data["vehicleId"]

    if vehicle_id not in VEHICLES:
        return jsonify({"error": "veicolo sconosciuto"}), 404

    try:
        response = requests.post(
            f"{VEHICLES[vehicle_id]}/tracking/start"
        )

        return jsonify({
            "status": "ok",
            "vehicleId": vehicle_id,
            "vehicleResponse": response.text
        })

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "impossibile contattare il veicolo"
        }), 500


# =========================
# ARRESTO TRACCIAMENTO
# =========================

@app.route("/tracking/stop", methods=["POST"])
def tracking_stop():

    data = request.get_json()

    if not data or "vehicleId" not in data:
        return jsonify({"error": "vehicleId mancante"}), 400

    vehicle_id = data["vehicleId"]

    if vehicle_id not in VEHICLES:
        return jsonify({"error": "veicolo sconosciuto"}), 404

    try:
        response = requests.post(
            f"{VEHICLES[vehicle_id]}/tracking/stop"
        )

        return jsonify({
            "status": "ok",
            "vehicleId": vehicle_id,
            "vehicleResponse": response.text
        })

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "impossibile contattare il veicolo"
        }), 500


# =========================
# ESECUZIONE
# =========================

if __name__ == "__main__":
    app.run(debug=True)