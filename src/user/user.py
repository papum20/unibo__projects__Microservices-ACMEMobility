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
URL_STATION_01_HW		= get_env_or_exit("URL_STATION_HW_01")
URL_STATION_02_HW		= get_env_or_exit("URL_STATION_HW_02")
URL_STATION_03_HW		= get_env_or_exit("URL_STATION_HW_03")
URL_STATION_04_HW		= get_env_or_exit("URL_STATION_HW_04")
URL_STATION_05_HW		= get_env_or_exit("URL_STATION_HW_05")
URL_VEHICLE_01			= get_env_or_exit("URL_VEHICLE_01")
URL_VEHICLE_02			= get_env_or_exit("URL_VEHICLE_02")
URL_VEHICLE_03			= get_env_or_exit("URL_VEHICLE_03")
URL_VEHICLE_04			= get_env_or_exit("URL_VEHICLE_04")
URL_VEHICLE_05			= get_env_or_exit("URL_VEHICLE_05")
URL_VEHICLE_06			= get_env_or_exit("URL_VEHICLE_06")
URL_VEHICLE_07			= get_env_or_exit("URL_VEHICLE_07")
URL_VEHICLE_08			= get_env_or_exit("URL_VEHICLE_08")
URL_VEHICLE_09			= get_env_or_exit("URL_VEHICLE_09")
URL_VEHICLE_10			= get_env_or_exit("URL_VEHICLE_10")
EP_STATION_HW_INSERT	= get_env_or_exit("ENDPOINT_STATION_HW_INSERT")
EP_VEHICLE_SIM_THEFT	= get_env_or_exit("ENDPOINT_VEHICLE_SIM_THEFT")

STATION_01_ID = get_env_or_exit("STATION_ID_01")
STATION_02_ID = get_env_or_exit("STATION_ID_02")
STATION_03_ID = get_env_or_exit("STATION_ID_03")
STATION_04_ID = get_env_or_exit("STATION_ID_04")
STATION_05_ID = get_env_or_exit("STATION_ID_05")

VEHICLE_01_ID	= get_env_or_exit("VEHICLE_ID_01")
VEHICLE_02_ID	= get_env_or_exit("VEHICLE_ID_02")
VEHICLE_03_ID	= get_env_or_exit("VEHICLE_ID_03")
VEHICLE_04_ID	= get_env_or_exit("VEHICLE_ID_04")
VEHICLE_05_ID	= get_env_or_exit("VEHICLE_ID_05")
VEHICLE_06_ID	= get_env_or_exit("VEHICLE_ID_06")
VEHICLE_07_ID	= get_env_or_exit("VEHICLE_ID_07")
VEHICLE_08_ID	= get_env_or_exit("VEHICLE_ID_08")
VEHICLE_09_ID	= get_env_or_exit("VEHICLE_ID_09")
VEHICLE_10_ID	= get_env_or_exit("VEHICLE_ID_10")

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

VEHICLE_ID_URL_MAP = {
	VEHICLE_01_ID: URL_VEHICLE_01,
	VEHICLE_02_ID: URL_VEHICLE_02,
	VEHICLE_03_ID: URL_VEHICLE_03,
	VEHICLE_04_ID: URL_VEHICLE_04,
	VEHICLE_05_ID: URL_VEHICLE_05,
	VEHICLE_06_ID: URL_VEHICLE_06,
	VEHICLE_07_ID: URL_VEHICLE_07,
	VEHICLE_08_ID: URL_VEHICLE_08,
	VEHICLE_09_ID: URL_VEHICLE_09,
	VEHICLE_10_ID: URL_VEHICLE_10
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
	print("Actions: scan, reserve, cancel, scan_reserved, park, lock, lock_assistance, steal")
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

	elif action == "lock_assistance":
		send_message(MESSAGE_USER_ASSISTANCE_LOCK, vehicle_id, user_id)
	
	elif action == "steal":

		# Simulate theft
		resp = requests.post(f"{VEHICLE_ID_URL_MAP.get(vehicle_id)}{EP_VEHICLE_SIM_THEFT}", timeout=REQUEST_TIMEOUT_SECONDS,
			json={})
		print(f"Simulate theft response: {resp.status_code} - {resp.text}")
		if resp.status_code != 200:
			sys.exit(1)

	else:
		print("Unknown action.")
		print_usage()