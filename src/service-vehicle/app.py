import time
import threading
from flask import Flask, jsonify, request
import requests

from geopy.distance import geodesic
from get_env import get_env_or_exit
from vehicle_status import VehicleStatus



app = Flask(__name__)


REQUEST_TIMEOUT_SECONDS = 10
SPEED_KMH				= 30
THEFT_LATLON_DIFF		= (1, 1)
THEFT_SPEED_KMH			= 100
UPDATE_TIMER_S			= 5

# "Firmware" Configuration loaded docker-compose environment
VEHICLE_ID		= get_env_or_exit('VEHICLE_ID')
URL_FLEET		= get_env_or_exit('URL_FLEET')
URL_GRAPHHOPPER = get_env_or_exit('URL_GRAPHHOPPER')
STATION_ID_01	= get_env_or_exit('URL_STATION_01')
STATION_ID_02	= get_env_or_exit('URL_STATION_02')
STATION_ID_03	= get_env_or_exit('URL_STATION_03')
STATION_ID_04	= get_env_or_exit('URL_STATION_04')
STATION_ID_05	= get_env_or_exit('URL_STATION_05')
STATION_PREFIX	= get_env_or_exit('STATION_PREFIX')
VEHICLE_PREFIX	= get_env_or_exit('VEHICLE_PREFIX')


# get starting station
VEHICLE_SUFFIX			= VEHICLE_ID.split(VEHICLE_PREFIX)[1] 
START_STATION_VAR_NAME	= f"VEHICLE_{VEHICLE_SUFFIX}_START_STATION"
START_STATION_ID		= get_env_or_exit(START_STATION_VAR_NAME)

# get starting coordinates
STATION_SUFFIX			= START_STATION_ID.split(STATION_PREFIX)[1]
STATION_LAT_VAR_NAME	= f"COORD_STATION_{STATION_SUFFIX}_LAT"
STATION_LON_VAR_NAME	= f"COORD_STATION_{STATION_SUFFIX}_LON"
START_LAT				= get_env_or_exit(STATION_LAT_VAR_NAME)
START_LON				= get_env_or_exit(STATION_LON_VAR_NAME)


is_tracking			= False
route_coordinates	= []
route_end_latlon	: tuple[float, float] | None	= None
route_start_latlon	: tuple[float, float]			= (float(START_LAT), float(START_LON))

# state for speed calculation
last_latlon		= route_start_latlon
last_time_s		= 0
last_route_idx	= 0
last_speed_kmh	= 0




def get_route_from_graphhopper(start_latlon, end_latlon):
	# ask Graphhopper for the route. 'points_encoded=false' gives us raw GPS arrays
	url = f"{URL_GRAPHHOPPER}/route?point={start_latlon}&point={end_latlon}&vehicle=car&points_encoded=false"
	
	response	= requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
	data		= response.json()
	# graphhopper returns coordinates as [longitude, latitude]
	coordinates = data["paths"][0]["points"]["coordinates"]
	
	# return the list of points, to iterate over
	return coordinates


@app.route('/start', methods=['POST'])
def start():

	if route_end_latlon is None:
		return jsonify({
			"success": False,
			"message": "Route end not set. Please set it via /simulate/end before starting tracking."
		}), 400

	# fetch route
	global route_coordinates
	global last_route_idx
	route_coordinates	= get_route_from_graphhopper(last_latlon, route_end_latlon)
	last_time			= time.time_ns() * 1e-9
	last_route_idx		= 0

	global is_tracking
	is_tracking = True
	print(f"[{VEHICLE_ID}] Tracking STARTED.")

	return jsonify({
			"success": True,
			"trackingActive": is_tracking,
			"message": f"Vehicle {VEHICLE_ID} is now being tracked."
		}), 200


@app.route('/stop', methods=['POST'])
def stop():

	route_coordinates.clear()
	global last_route_idx
	last_route_idx = 0

	global is_tracking
	is_tracking = False
	
	print(f"[{VEHICLE_ID}] Tracking STOPPED.")
	return jsonify({
			"success": True,
			"trackingActive": is_tracking,
			"message": f"Vehicle {VEHICLE_ID} is no longer being tracked."
		}), 200



# set route end
@app.route('/simulate/end', methods=['POST'])
def simulate_route_end():
	data = request.get_json()
	if not data:
		return jsonify({"error": "Invalid JSON"}), 400

	end_latlon = data.get("endLatLon")
	if not end_latlon:
		return jsonify({"error": "endLatLon is required"}), 400
	global route_end_latlon
	route_end_latlon = tuple(end_latlon)
	
	return jsonify({
		"success": True,
		"message": f"Route end set to {end_latlon}"
	}), 200


def update_position(latlon, speed_kmh, status):
	payload = {
		"vehicleId"		: VEHICLE_ID,
		"coordinates"	: {
			"latitude"	: latlon[0],
			"longitude"	: latlon[1]
		},
		"speedKmH"	: speed_kmh,
		"status"	: status
	}

	try:
		target_url = f"{URL_FLEET}/tracking/position/{VEHICLE_ID}"
		requests.put(target_url, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
		print(f"[{VEHICLE_ID}] Pushed GPS to {target_url}")
		return jsonify({"success": True}), 200
	except Exception as e:
		print(f"[{VEHICLE_ID}] Network error: {e}")
		return jsonify({"success": False, "message": "Network error"}), 503


# Makes a vehicle start moving without ACME knowing
@app.route('/simulate/force_move', methods=['POST'])
def simulate_theft():
	next_latlon = (last_latlon[0] + THEFT_LATLON_DIFF[0], last_latlon[1] + THEFT_LATLON_DIFF[1])
	return update_position(next_latlon, THEFT_SPEED_KMH, VehicleStatus.MOVING)


def tracking_loop():
	global last_latlon
	global last_route_idx
	global last_speed_kmh
	global last_time_s
	
	while True:
		if is_tracking:

			curr_time		= time.time_ns() * 1e-9
			diff_time		= curr_time - last_time_s
			dist_at_speed	= (SPEED_KMH / 3600) * diff_time
			next_dist		= 0
			next_latlon		= last_latlon

			while True:
				if last_route_idx == len(route_coordinates) - 1:
					print(f"[{VEHICLE_ID}] Reached route end.")
					break
				
				next_latlon = (
					route_coordinates[last_route_idx][1],
					route_coordinates[last_route_idx][0]
				)
				# expects (lat, lon)
				next_dist	= geodesic(last_latlon, next_latlon).kilometers

				if next_dist < dist_at_speed:
					# move to next point and keep checking
					last_route_idx += 1


			speed_kmh	= next_dist / diff_time * 3600 if diff_time > 0 else 0
			status		= VehicleStatus.MOVING if speed_kmh > 0 else VehicleStatus.HALTED
			
			update_position(next_latlon, speed_kmh, status)

			last_latlon		= next_latlon
			last_speed_kmh	= speed_kmh
			last_time_s		= curr_time
				
		time.sleep(UPDATE_TIMER_S)



if __name__ == '__main__':
	# Start the hardware background loop
	threading.Thread(target=tracking_loop, daemon=True).start()
	# Start listening for incoming commands on port 6000
	app.run(host='0.0.0.0', port=6000)
