import logging
import time
import threading
from flask import Flask, jsonify, request
import requests

from geopy.distance import geodesic
from get_env import get_env_or_exit
from vehicle_status import VehicleStatus



app = Flask(__name__)
logger = logging.getLogger(__name__)


REQUEST_TIMEOUT_SECONDS = 10
SPEED_KMH				= 30
THEFT_LATLON_DIFF		= (1, 1)
THEFT_SPEED_KMH			= 100
UPDATE_TIMER_S			= 5

# "Firmware" Configuration loaded docker-compose environment
VEHICLE_ID		= get_env_or_exit('VEHICLE_ID')
URL_FLEET		= get_env_or_exit('URL_FLEET')
URL_GRAPHHOPPER = get_env_or_exit('URL_GRAPHHOPPER')
PORT_VEHICLES	= int(get_env_or_exit('PORT_VEHICLES'))
STATION_ID_01	= get_env_or_exit('URL_STATION_01')
STATION_ID_02	= get_env_or_exit('URL_STATION_02')
STATION_ID_03	= get_env_or_exit('URL_STATION_03')
STATION_ID_04	= get_env_or_exit('URL_STATION_04')
STATION_ID_05	= get_env_or_exit('URL_STATION_05')
STATION_PREFIX	= get_env_or_exit('STATION_PREFIX')
VEHICLE_PREFIX	= get_env_or_exit('VEHICLE_PREFIX')

# get starting station
VEHICLE_SUFFIX			= VEHICLE_ID.split(f'{VEHICLE_PREFIX}-')[1] 
START_STATION_VAR_NAME	= f"VEHICLE_{VEHICLE_SUFFIX}_START_STATION"
START_STATION_ID		= get_env_or_exit(START_STATION_VAR_NAME)
logger.info("Vehicle %s. Start station %s.", VEHICLE_ID, START_STATION_ID)

# get ending station
END_STATION_VAR_NAME	= f"VEHICLE_{VEHICLE_SUFFIX}_END_STATION"
END_STATION_ID			= get_env_or_exit(END_STATION_VAR_NAME)

# get starting coordinates
_station_suffix			= START_STATION_ID.split(f'{STATION_PREFIX}-')[1]
_station_number			= _station_suffix.split('-')[1]
_station_lat_var_name	= f"COORD_STATION_{_station_number}_LAT"
_station_lon_var_name	= f"COORD_STATION_{_station_number}_LON"
START_LAT				= get_env_or_exit(_station_lat_var_name)
START_LON				= get_env_or_exit(_station_lon_var_name)

# get ending coordinates
_station_suffix			= END_STATION_ID.split(f'{STATION_PREFIX}-')[1]
_station_number			= _station_suffix.split('-')[1]
_station_lat_var_name	= f"COORD_STATION_{_station_number}_LAT"
_station_lon_var_name	= f"COORD_STATION_{_station_number}_LON"
END_LAT					= get_env_or_exit(_station_lat_var_name)
END_LON					= get_env_or_exit(_station_lon_var_name)


is_tracking			= False
route_coordinates	= []
route_end_latlon	: tuple[float, float]	= (float(END_LAT), float(END_LON))
route_start_latlon	: tuple[float, float]	= (float(START_LAT), float(START_LON))

# state for speed calculation
last_latlon		= route_start_latlon
last_time_s		= 0
last_route_idx	= 0
last_speed_kmh	= 0




def get_route_from_graphhopper(start_latlon, end_latlon):
	start_str	= f"{start_latlon[0]},{start_latlon[1]}"
	end_str		= f"{end_latlon[0]},{end_latlon[1]}"
	# ask Graphhopper for the route. 'points_encoded=false' gives raw GPS arrays (lon,lat)
	url			= f"{URL_GRAPHHOPPER}/route?point={start_str}&point={end_str}&profile=car&points_encoded=false"
	
	response	= requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)

	if response.status_code != 200:
		logger.error("[%s] Graphhopper Error: %s", VEHICLE_ID, response.text)
		return None

	data		= response.json()
	# graphhopper returns coordinates as [longitude, latitude]
	coordinates = data["paths"][0]["points"]["coordinates"]
	
	logger.info("[%s] Graphhopper route from %s to %s: %d points", VEHICLE_ID, start_latlon, end_latlon, len(coordinates))

	# return the list of points, to iterate over
	return coordinates


@app.route('/tracking/start', methods=['POST'])
def start():

	if route_end_latlon is None:
		return jsonify({
			"success": False,
			"message": "Route end not set. Please set it via /simulate/end before starting tracking."
		}), 400

	# fetch route
	global route_coordinates
	global last_time_s
	global last_route_idx
	route	= get_route_from_graphhopper(last_latlon, route_end_latlon)

	if not route:
		logger.error("Graphhopper routing failed (vehicle %s). Check coordinates and map.", VEHICLE_ID)
		return jsonify({"success": False, "message": "Graphhopper routing failed. Check coordinates and map."}), 500

	route_coordinates	= route
	last_time_s			= time.time_ns() * 1e-9
	last_route_idx		= 0

	global is_tracking
	is_tracking = True
	logger.info("[%s] Tracking STARTED.", VEHICLE_ID)

	return jsonify({
			"success": True,
			"trackingActive": is_tracking,
			"message": f"Vehicle {VEHICLE_ID} is now being tracked."
		}), 200


@app.route('/tracking/stop', methods=['POST'])
def stop():

	route_coordinates.clear()
	global last_route_idx
	last_route_idx = 0

	global is_tracking
	is_tracking = False
	
	logger.info("[%s] Tracking STOPPED.", VEHICLE_ID)
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


def update_position(latlon, speed_kmh, status: str, time_epoch_s: float) -> bool:
	"""
	@return True in case of success
	"""
	payload = {
		"coordinates"	: {
			"latitude"	: latlon[0],
			"longitude"	: latlon[1]
		},
		"speedKmH"	: speed_kmh,
		"status"	: status,
		"timeEpochS": time_epoch_s
	}

	try:
		target_url = f"{URL_FLEET}/tracking/position/{VEHICLE_ID}"
		response = requests.post(target_url, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)

		if response.status_code in [200, 204]:
			logger.info("[%s] Pushed GPS to %s", VEHICLE_ID, target_url)
			return True
		else:
			logger.error("[%s] Fleet Tracking rejected data: %s", VEHICLE_ID, response.text)
	except Exception as e:
		logger.error("[%s] Network error: %s", VEHICLE_ID, e)
	return False

# Makes a vehicle start moving without ACME knowing
@app.route('/simulate/force_move', methods=['POST'])
def simulate_theft():
	next_latlon = (last_latlon[0] + THEFT_LATLON_DIFF[0], last_latlon[1] + THEFT_LATLON_DIFF[1])
	res = update_position(next_latlon, THEFT_SPEED_KMH, VehicleStatus.MOVING.name, time.time_ns() * 1e-9)
	if res:
		logger.warning("[%s] Simulated theft: vehicle moved to %s at %s km/h", VEHICLE_ID, next_latlon, THEFT_SPEED_KMH)
		return jsonify({
			"success": True,
			"message": f"Vehicle {VEHICLE_ID} simulated theft: moved to {next_latlon} at {THEFT_SPEED_KMH} km/h"
		}), 200
	else:
		logger.error("[%s] Simulated theft failed: could not update position", VEHICLE_ID)
		return jsonify({
			"success": False,
			"message": f"Vehicle {VEHICLE_ID} simulated theft failed: could not update position"
		}), 500


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
					logger.info("[%s] Reached route end.", VEHICLE_ID)
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
				else:
					# next point is too far, stay at last_latlon
					break


			speed_kmh	= next_dist / diff_time * 3600 if diff_time > 0 else 0
			status		= VehicleStatus.MOVING.name if speed_kmh > 0 else VehicleStatus.HALTED.name
			
			update_position(next_latlon, speed_kmh, status, curr_time)

			last_latlon		= next_latlon
			last_speed_kmh	= speed_kmh
			last_time_s		= curr_time
				
		time.sleep(UPDATE_TIMER_S)



if __name__ == '__main__':
	# Start the hardware background loop
	threading.Thread(target=tracking_loop, daemon=True).start()
	# Start listening for incoming commands
	app.run(host='0.0.0.0', port=PORT_VEHICLES)
