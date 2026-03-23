import os
import requests
import sys
import json
from pathlib import Path
from dotenv import load_dotenv



# expected .env in the parent directory of this file
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def get_env_or_exit(key: str) -> str:
	val = os.environ.get(key)
	if val is None:
		print(f"Missing required environment variable (make sure .env is configured in the parent directory): {key}", file=sys.stderr)
		sys.exit(2)
	return val

URL_CAMUNDA_MESSAGE = get_env_or_exit("URL_CAMUNDA_MESSAGE")

MESSAGE_USER_START_IMMEDIATE	= get_env_or_exit("MESSAGE_USER_START_IMMEDIATE")
MESSAGE_USER_START_RESERVE		= get_env_or_exit("MESSAGE_USER_START_RESERVE")
MESSAGE_USER_CANCEL				= get_env_or_exit("MESSAGE_USER_CANCEL")
MESSAGE_USER_RESERVE_SCAN		= get_env_or_exit("MESSAGE_USER_RESERVE_SCAN")
MESSAGE_USER_PARKED				= get_env_or_exit("MESSAGE_USER_PARKED")



def send_message(message_name, vehicle_id, variables=None):
	payload = {
		"messageName": message_name,
		"businessKey": vehicle_id, # Link actions to this specific vehicle
		"processVariables": {
			"vehicleId": {"value": vehicle_id, "type": "String"}
		}
	}
	
	if variables:
		for k, v in variables.items():
			v_type = "Boolean" if isinstance(v, bool) else "String"
			payload["processVariables"][k] = {"value": v, "type": v_type}

	response = requests.post(URL_CAMUNDA_MESSAGE, json=payload)
	
	if response.status_code in [200, 204]:
		print(f"Success: {message_name} sent for {vehicle_id}")
	else:
		print(f"Error {response.status_code}: {response.text}")



def print_usage():
	print("\nUsage: python user_actions.py [action] [vehicle_id]")
	print("Actions: scan, reserve, cancel, scan_reserved, park")
	print("Example: python user_actions.py scan V-001\n")



if __name__ == "__main__":
	if len(sys.argv) < 3:
		print_usage()
		sys.exit(1)

	action = sys.argv[1]
	vid = sys.argv[2]


	if action == "scan":
		send_message(MESSAGE_USER_START_IMMEDIATE, vid, variables={"isImmediate": True})
	
	elif action == "reserve":
		# We add a timestamp for the cancellation logic
		send_message(MESSAGE_USER_START_RESERVE, vid, variables={"isImmediate": False})
	
	elif action == "cancel":
		send_message(MESSAGE_USER_CANCEL, vid)
	
	elif action == "scan_reserved":
		send_message(MESSAGE_USER_RESERVE_SCAN, vid)
	
	elif action == "park":
		send_message(MESSAGE_USER_PARKED, vid)
	
	else:
		print("Unknown action.")
		print_usage()