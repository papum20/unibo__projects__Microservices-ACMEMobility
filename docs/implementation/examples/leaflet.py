# In Fleet Gateway


latest_positions = {}

@app.route('/tracking/position/<vehicle_id>', methods=['PUT'])
def update_position(vehicle_id):
    latest_positions[vehicle_id] = request.json
    return jsonify({"success": True})

# NEW ENDPOINT FOR THE MAP
@app.route('/tracking/all', methods=['GET'])
def get_all_positions():
    return jsonify(latest_positions)