import os
import requests
import sys
from pathlib import Path
from dotenv import load_dotenv



# expected .env in the parent directory
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def get_env_or_exit(key: str) -> str:
	val = os.environ.get(key)
	if val is None:
		print(f"Missing required environment variable (make sure .env is configured in the parent directory): {key}", file=sys.stderr)
		sys.exit(2)
	return val

URL_CAMUNDA_MESSAGE		= get_env_or_exit("URL_CAMUNDA_MESSAGE")
URL_STATION_01_HW		= get_env_or_exit("URL_STATION_01_HW")
URL_STATION_02_HW		= get_env_or_exit("URL_STATION_02_HW")
URL_STATION_03_HW		= get_env_or_exit("URL_STATION_03_HW")
URL_STATION_04_HW		= get_env_or_exit("URL_STATION_04_HW")
URL_STATION_05_HW		= get_env_or_exit("URL_STATION_05_HW")
EP_STATION_HW_INSERT	= get_env_or_exit("ENDPOINT_STATION_HW_INSERT")

STATION_01_ID = get_env_or_exit("STATION_ID_01")
STATION_02_ID = get_env_or_exit("STATION_ID_02")
STATION_03_ID = get_env_or_exit("STATION_ID_03")
STATION_04_ID = get_env_or_exit("STATION_ID_04")
STATION_05_ID = get_env_or_exit("STATION_ID_05")

MESSAGE_USER_START_IMMEDIATE	= get_env_or_exit("MESSAGE_USER_START_IMMEDIATE")
MESSAGE_USER_START_RESERVE		= get_env_or_exit("MESSAGE_USER_START_RESERVE")
MESSAGE_USER_CANCEL				= get_env_or_exit("MESSAGE_USER_CANCEL")
MESSAGE_USER_RESERVE_SCAN		= get_env_or_exit("MESSAGE_USER_RESERVE_SCAN")
MESSAGE_USER_LOCKED				= get_env_or_exit("MESSAGE_USER_LOCKED")
MESSAGE_USER_ASSISTANCE_LOCK	= get_env_or_exit("MESSAGE_USER_ASSISTANCE_LOCK")

STATION_ID_URL_MAP = {
	STATION_01_ID: URL_STATION_01_HW,
	STATION_02_ID: URL_STATION_02_HW,
	STATION_03_ID: URL_STATION_03_HW,
	STATION_04_ID: URL_STATION_04_HW,
	STATION_05_ID: URL_STATION_05_HW
}

REQUEST_TIMEOUT_SECONDS = 10



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
	print("Actions: scan, reserve, cancel, scan_reserved, park, lock, lock-assistance")
	print("Example: python user.py scan u001 v001")
	print("Example: python user.py park u001 v001 s001\n")



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
		hardware_resp = requests.post(f"{STATION_ID_URL_MAP.get(station_id)}{EP_STATION_HW_INSERT}", timeout=REQUEST_TIMEOUT_SECONDS,
			json={
				"vehicleId": vehicle_id
			})
		if hardware_resp.status_code == 200:
			print(f"Hardware sensor detected {vehicle_id} at {station_id}!")
		else:
			print(f"Physical insertion failed: {hardware_resp.text}")
			sys.exit(1)
	
	elif action == "lock":
		if len(sys.argv) < 5:
			print_usage()
			sys.exit(1)
		station_id = sys.argv[4]

		send_message(MESSAGE_USER_LOCKED, vehicle_id, user_id, variables={"stationId": station_id})

	elif action == "lock-assistance":
		send_message(MESSAGE_USER_ASSISTANCE_LOCK, vehicle_id, user_id)
	
	else:
		print("Unknown action.")
		print_usage()