import requests
import sys
from pathlib import Path
from dotenv import load_dotenv

from get_env import get_env_or_exit



# expected .env in the parent directory
load_dotenv(Path(__file__).resolve().parents[1] / ".env")



STATION_PREFIX		= get_env_or_exit('STATION_PREFIX')
STATION_N			= int(get_env_or_exit('STATION_N'))
STATION_DIGITS		= int(get_env_or_exit('STATION_DIGITS'))
VEHICLE_PREFIX      = get_env_or_exit('VEHICLE_PREFIX')
VEHICLE_N			= int(get_env_or_exit('VEHICLE_N'))
VEHICLE_DIGITS		= int(get_env_or_exit('VEHICLE_DIGITS'))

URL_CAMUNDA_MESSAGE		= get_env_or_exit("URL_CAMUNDA_MESSAGE")
URL_STATION_PARAM_LOCAL	= get_env_or_exit('URL_STATION_PARAM_LOCAL')
URL_VEHICLE_PARAM_LOCAL	= get_env_or_exit('URL_VEHICLE_PARAM_LOCAL')
EP_STATION_HW_INSERT	= get_env_or_exit("ENDPOINT_STATION_HW_INSERT")
EP_VEHICLE_SIM_STATION	= get_env_or_exit("ENDPOINT_VEHICLE_SIM_STATION")
EP_VEHICLE_SIM_THEFT	= get_env_or_exit("ENDPOINT_VEHICLE_SIM_THEFT")

PORT_LOCAL_STATION_MAP = {
	str(i).zfill(STATION_DIGITS):
		get_env_or_exit(f'PORT_LOCAL_STATION_{str(i).zfill(STATION_DIGITS)}') for i in range(1, STATION_N + 1)
}
PORT_LOCAL_VEHICLE_MAP = {
	str(i).zfill(VEHICLE_DIGITS):
		get_env_or_exit(f'PORT_LOCAL_VEHICLE_{str(i).zfill(VEHICLE_DIGITS)}') for i in range(1, VEHICLE_N + 1)
}

MESSAGE_USER_START_IMMEDIATE	= get_env_or_exit("MESSAGE_USER_START_IMMEDIATE")
MESSAGE_USER_START_RESERVE		= get_env_or_exit("MESSAGE_USER_START_RESERVE")
MESSAGE_USER_CANCEL				= get_env_or_exit("MESSAGE_USER_CANCEL")
MESSAGE_USER_RESERVE_SCAN		= get_env_or_exit("MESSAGE_USER_RESERVE_SCAN")
MESSAGE_USER_LOCKED				= get_env_or_exit("MESSAGE_USER_LOCKED")
MESSAGE_USER_ASSISTANCE_LOCK	= get_env_or_exit("MESSAGE_USER_ASSISTANCE_LOCK")

CAMUNDA_TIMER_EVENT_ID = "Event_0s7sh38"

REQUEST_TIMEOUT_SECONDS = 10


def get_vehicle_url(vehicle_id: str) -> str:
	vehicle_suffix	= vehicle_id.rsplit(f'{VEHICLE_PREFIX}-', 1)[-1]
	vehicle_number	= vehicle_suffix
	return URL_VEHICLE_PARAM_LOCAL.replace("{vehiclePort}", PORT_LOCAL_VEHICLE_MAP[vehicle_number])

def get_station_url(station_id: str) -> str:
	station_suffix = station_id.rsplit(f'{STATION_PREFIX}-', 1)[-1]
	station_number = station_suffix.rsplit("-", 1)[-1]
	return URL_STATION_PARAM_LOCAL.replace("{stationPort}", PORT_LOCAL_STATION_MAP[station_number])




def send_message(message_name, vehicle_id, user_id, variables=None):
	payload = {
		"messageName": message_name,
		"businessKey": vehicle_id,	# Used by Camunda to index process instances (e.g. to this specific vehicle)
		"processVariables": {
			"vehicleId": {"value": vehicle_id, "type": "String"},
			"userId": {"value": user_id, "type": "String"}
		}
	}
	
	if variables:
		for k, v in variables.items():
			v_type = "Boolean" if isinstance(v, bool) else "String"
			payload["processVariables"][k] = {"value": v, "type": v_type}

	response = requests.post(URL_CAMUNDA_MESSAGE, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
	
	if response.status_code in [200, 204]:
		print(f"Success: {message_name} sent for {vehicle_id}")
	else:
		print(f"Error {response.status_code}: {response.text}")



def print_usage():
	print("\nUsage: python user.py <action> <user_id> <vehicle_id> [station_id]")
	print("Actions: scan, reserve, cancel, scan_reserved, park, lock, lock_assistance, steal, force_timeout")
	print("Example: python user.py scan USER-001 V-01")
	print("Example: python user.py reserve USER-001 V-01")
	print("Example: python user.py cancel USER-001 V-01")
	print("Example: python user.py scan_reserved USER-001 V-01")
	print("Example: python user.py park USER-001 V-01 STATION-bologna-01")
	print("Example: python user.py lock USER-001 V-01 STATION-bologna-01")
	print("Example: python user.py lock_assistance USER-001 V-01")
	print("Example: python user.py steal USER-001 V-01")
	print("Example: python user.py force_timeout USER-001 V-01")
	print("")



if __name__ == "__main__":
	if len(sys.argv) < 4:
		print_usage()
		sys.exit(1)

	action			= sys.argv[1]
	user_id			= sys.argv[2]
	vehicle_id		= sys.argv[3]


	if action == "scan":
		send_message(MESSAGE_USER_START_IMMEDIATE, vehicle_id, user_id, variables={"isImmediate": True})
	
	elif action == "reserve":
		send_message(MESSAGE_USER_START_RESERVE, vehicle_id, user_id, variables={"isImmediate": False})
	
	elif action == "cancel":
		send_message(MESSAGE_USER_CANCEL, vehicle_id, user_id)
	
	elif action == "scan_reserved":
		send_message(MESSAGE_USER_RESERVE_SCAN, vehicle_id, user_id)
	
	elif action == "park":
		if len(sys.argv) < 5:
			print_usage()
			sys.exit(1)
		station_id = sys.argv[4]

		# Simulate the physical insertion into the station hardware
		hardware_resp = requests.post(f"{get_station_url(station_id)}{EP_STATION_HW_INSERT}", timeout=REQUEST_TIMEOUT_SECONDS,
			json={
				"vehicleId": vehicle_id
			})
		if hardware_resp.status_code == 200:
			print(f"Hardware sensor detected {vehicle_id} at {station_id}!")
		else:
			print(f"Physical insertion failed: {hardware_resp.text}")
			sys.exit(1)

		# Simulate the insertion on the vehicle side (i.e. set its position to the station)
		resp = requests.post(f"{get_vehicle_url(vehicle_id)}{EP_VEHICLE_SIM_STATION}", timeout=REQUEST_TIMEOUT_SECONDS,
			json={
				"stationId": station_id
			})
		if resp.status_code == 200:
			print(f"Success: Vehicle {vehicle_id} set to station {station_id}.")
		else:
			print(f"Failed to set vehicle station: {resp.text}")
			sys.exit(1)

	elif action == "lock":
		if len(sys.argv) < 5:
			print_usage()
			sys.exit(1)
		station_id = sys.argv[4]

		send_message(MESSAGE_USER_LOCKED, vehicle_id, user_id, variables={"stationId": station_id})

	elif action == "lock_assistance":
		send_message(MESSAGE_USER_ASSISTANCE_LOCK, vehicle_id, user_id, variables={"needsAssistance": True})
	
	elif action == "steal":

		# Simulate theft
		resp = requests.post(f"{get_vehicle_url(vehicle_id)}{EP_VEHICLE_SIM_THEFT}", timeout=REQUEST_TIMEOUT_SECONDS,
			json={})
		print(f"Simulate theft response: {resp.status_code} - {resp.text}")
		if resp.status_code != 200:
			sys.exit(1)

	elif action == "force_timeout":
		# Ask Camunda for any active jobs matching the vehicle's Business Key and the Timer Event ID
		jobs_url = f"http://localhost:8080/engine-rest/job?processInstanceBusinessKey={vehicle_id}&activityId={CAMUNDA_TIMER_EVENT_ID}"

		try:
			resp = requests.get(jobs_url, timeout=REQUEST_TIMEOUT_SECONDS)
			jobs = resp.json()
			
			if jobs:
				job_id = jobs[0]["id"]
				# Force Camunda to execute the timer job immediately
				execute_url = f"http://localhost:8080/engine-rest/job/{job_id}/execute"
				requests.post(execute_url, timeout=REQUEST_TIMEOUT_SECONDS)
				print("Success: Forced 30-minute timeout to expire immediately.")
			else:
				print("No active 30-minute reservation timer found.")
				
		except Exception as e:
			print(f"Failed to communicate with Camunda: {e}")

	else:
		print("Unknown action.")
		print_usage()