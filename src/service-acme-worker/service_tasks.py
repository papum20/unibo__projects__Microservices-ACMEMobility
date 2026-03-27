from datetime import datetime, timezone
import logging
import requests
import xml.etree.ElementTree as ET
from camunda.external_task.external_task import ExternalTask, TaskResult

from util import get_env_or_exit



# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read Configuration from Docker Environment
URL_CAMUNDA         = get_env_or_exit('URL_CAMUNDA')
URL_BANK_WSDL       = get_env_or_exit('URL_BANK_WSDL')
URL_STATION_BASE    = get_env_or_exit('URL_STATION')
URL_FLEET_BASE      = get_env_or_exit('URL_FLEET')
URL_BANK_BASE		= get_env_or_exit('URL_BANK')
URL_STATION_BASE	= get_env_or_exit('URL_STATION')

EP_BANK_PREAUTH			= get_env_or_exit('ENDPOINT_BANK_PREAUTH')
EP_BANK_CHARGE			= get_env_or_exit('ENDPOINT_BANK_CHARGE')
EP_BANK_UNLOCK_CAUTION	= get_env_or_exit('ENDPOINT_BANK_UNLOCK_CAUTION')

BANK_CAUTION        = int(get_env_or_exit('BANK_CAUTION'))

CAMUNDA_USER_ID					= get_env_or_exit('CAMUNDA_VAR_USER_ID')
CAMUNDA_VEHICLE_ID				= get_env_or_exit('CAMUNDA_VAR_VEHICLE_ID')
CAMUNDA_IS_IMMEDIATE			= get_env_or_exit('CAMUNDA_VAR_IS_IMMEDIATE')
CAMUNDA_RESERVE_TIME			= get_env_or_exit('CAMUNDA_VAR_RESERVE_TIME')
CAMUNDA_BANK_TOKEN				= get_env_or_exit('CAMUNDA_VAR_BANK_TOKEN')
CAMUNDA_AMOUNT_TO_CHARGE		= get_env_or_exit('CAMUNDA_VAR_AMOUNT_TO_CHARGE')
CAMUNDA_CONVERT_CAUTION_STATUS	= get_env_or_exit('CAMUNDA_VAR_CONVERT_CAUTION_STATUS')
CAMUNDA_CAUTION_BLOCKED			= get_env_or_exit('CAMUNDA_VAR_CAUTION_BLOCKED')
CAMUNDA_PAYMENT_STATUS			= get_env_or_exit('CAMUNDA_VAR_PAYMENT_STATUS')
CAMUNDA_BATTERY_LEVEL			= get_env_or_exit('CAMUNDA_VAR_BATTERY_LEVEL')
CAMUNDA_VEHICLE_UNLOCKED		= get_env_or_exit('CAMUNDA_VAR_VEHICLE_UNLOCKED')
CAMUNDA_CANCEL_MINUTES			= get_env_or_exit('CAMUNDA_VAR_CANCEL_MINUTES')
CAMUNDA_AMOUNT_BASE				= get_env_or_exit('CAMUNDA_VAR_AMOUNT_BASE')
CAMUNDA_PENALTY_APPLIED			= get_env_or_exit('CAMUNDA_VAR_PENALTY_APPLIED')


REQUEST_TIMEOUT_SECONDS = 10
REQUEST_MAX_RETRIES		= 3
REQUEST_RETRY_DELAY_MS	= 5000

SOAP_HEADERS = {'Content-Type': 'text/xml; charset=utf-8'}


def get_user_saved_card(user_id):
	"""Simulate fetching the user's saved card from a database or external service."""
	return f"USER-{user_id}-CARD-1234"

def get_soap_body(body_content: str) -> str:
	return f"""<?xml version="1.0" encoding="UTF-8"?>
		<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
			<SOAP-ENV:Body>
				{body_content}
			</SOAP-ENV:Body>
		</SOAP-ENV:Envelope>"""

def soap_request(url: str, data: str) -> requests.Response:
	"""throws requests.exceptions.Timeout if the request takes too long"""
	return requests.post(url, data=data, headers=SOAP_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)



def handle_config(task: ExternalTask) -> TaskResult:
	logger.info("Received config request for Process Instance: %s", task.get_process_instance_id())

	# Define Endpoints (API Paths)
	# These are the specific paths for your Jolie/Python services
	# You can change them here if your API signature changes
	
	# Bank Endpoints
	ep_bank_preauth = "/preAuth"
	ep_bank_charge  = "/charge"
	ep_bank_unlock  = "/unlock"

	# Station Endpoints
	ep_station_unlock = "/vehicle/unlock"
	ep_station_lock   = "/vehicle/lock"
	
	# Fleet Endpoints (Assuming standard REST paths)
	ep_fleet_track_start	= "/vehicle/track-start"
	ep_fleet_track_status   = "/vehicle/track-status"
	ep_fleet_battery        = "/vehicle/battery"

	# 3. Pack everything into variables for Camunda
	# We send both Base URLs and Endpoints separately
	config_variables = {
		# Base URLs
		"urlBank": URL_BANK_BASE,
		"urlStation": URL_STATION_BASE,

		# Bank
		"epBankPreAuth": ep_bank_preauth,
		"epBankCharge": ep_bank_charge,
		"epBankUnlock": ep_bank_unlock,
		"valBankCaution": BANK_CAUTION,

		# Station
		"epStationUnlock": ep_station_unlock,
		"epStationLock": ep_station_lock,
		
		# Fleet (Example)
		"epFleetTrackStart": ep_fleet_track_start,
		"epFleetTrackStatus": ep_fleet_track_status,
		"epFleetBattery": ep_fleet_battery
	}

	logger.info("Injecting configuration: %s", config_variables)

	# 4. Complete the task and inject variables into the Process Scope
	return task.complete(global_variables=config_variables)



# =====================================================================
# BANK SERVICES (JOLIE - SOAP via Zeep)
# =====================================================================

def handle_bank_preauth(task: ExternalTask) -> TaskResult:
	"""Topic: bank-preauth (block 10€ caution money)"""
	logger.info("Executing SOAP PreAuth for process %s", task.get_process_instance_id())
	
	card_id		= get_user_saved_card(task.get_variable(CAMUNDA_USER_ID))
	soap_body	= get_soap_body(
		f"""<preAuth>
			<cardId>{card_id}</cardId>
			<amount>{BANK_CAUTION}</amount>
		</preAuth>""")
	
	try:
		response = soap_request(URL_BANK_WSDL, soap_body)
		
		if response.status_code == 200:
			root = ET.fromstring(response.content)
			
			# search for the tags, ignoring namespaces, using ".//"
			token_element   = root.find(".//token")
			success_element = root.find(".//success")
			
			if token_element is not None:
				token   = token_element.text
				success = (success_element.text == 'true')  # type: ignore
				
				logger.info("Bank PreAuth Success! Token: %s", token)
				
				# Save the token to Camunda variables
				return task.complete({
					CAMUNDA_BANK_TOKEN		: token,
					CAMUNDA_CAUTION_BLOCKED	: success
				})
			else:
				return task.failure("Parse Error", "Could not find <token> in SOAP response", 0, 0)
		else:
			return task.failure("SOAP HTTP Error", f"Code {response.status_code}", 0, 0)
	except requests.exceptions.Timeout:
		logger.error("Bank service timed out!")
		return task.failure(
			error_message="Bank Service Timeout", 
			error_details="The bank service took more than 10 seconds to respond.",
			max_retries=REQUEST_MAX_RETRIES, 
			retry_timeout=REQUEST_RETRY_DELAY_MS
		)
	except Exception as e:
		logger.error("Connection Error: %s", e)
		return task.failure("Connection Error", str(e), 0, 0)


def handle_bank_charge(task: ExternalTask) -> TaskResult:
	"""Topic: bank-charge (charge user)"""
	logger.info("Executing SOAP Charge")
	# Get variables from Camunda context
	token		= task.get_variable(CAMUNDA_BANK_TOKEN)
	amount		= task.get_variable(CAMUNDA_AMOUNT_TO_CHARGE)
	soap_body	= get_soap_body(
		f"""<charge>
			<token>{token}</token>
			<amount>{amount}</amount>
		</charge>""")
	
	try:
		response = soap_request(URL_BANK_WSDL, soap_body)

		if response.status_code == 200:
			root = ET.fromstring(response.content)
			status_element = root.find(".//status")
			
			if status_element is not None:
				status = status_element.text
				logger.info("Bank Charge Status: %s", status)
				
				return task.complete({CAMUNDA_PAYMENT_STATUS: status})
			else:
				return task.failure("Parse Error", "Could not find <status> in SOAP response", 0, 0)
		else:
			return task.failure("SOAP HTTP Error", f"Code {response.status_code}", 0, 0)
	except requests.exceptions.Timeout:
		logger.error("Bank service timed out!")
		return task.failure(
			error_message="Bank Service Timeout", 
			error_details="The bank service took more than 10 seconds to respond.",
			max_retries=REQUEST_MAX_RETRIES, 
			retry_timeout=REQUEST_RETRY_DELAY_MS
		)
	except Exception as e:
		logger.error("SOAP Error in Charge: %s", e)
		return task.failure(error_message="Charge Failed", error_details=str(e), max_retries=0, retry_timeout=0)
		

def handle_bank_unlock_caution(task: ExternalTask) -> TaskResult:
	"""Topic: bank-unlock-caution"""
	logger.info("Executing SOAP Unlock Caution")

	token		= task.get_variable(CAMUNDA_BANK_TOKEN)
	soap_body	= get_soap_body(
		f"""<unlockCaution>
			<token>{token}</token>
		</unlockCaution>""")

	try:
		response = soap_request(URL_BANK_WSDL, soap_body)

		if response.status_code == 200:
			root = ET.fromstring(response.content)
			success_element = root.find(".//success")
			
			if success_element is not None:
				success = (success_element.text == 'true')  # type: ignore
				logger.info("Bank Unlock Caution Success: %s", success)
				return task.complete({"cautionUnlocked": success})
			else:
				return task.failure("Parse Error", "Could not find <success> in SOAP response", 0, 0)
		else:
			return task.failure("SOAP HTTP Error", f"Code {response.status_code}", 0, 0)
	except requests.exceptions.Timeout:
		logger.error("Bank service timed out!")
		return task.failure(
			error_message="Bank Service Timeout", 
			error_details="The bank service took more than 10 seconds to respond.",
			max_retries=REQUEST_MAX_RETRIES, 
			retry_timeout=REQUEST_RETRY_DELAY_MS
		)
	except Exception as e:
		logger.error("SOAP Error in Unlock Caution: %s", e)
		return task.failure(error_message="Unlock Caution Failed", error_details=str(e), max_retries=0, retry_timeout=0)


def handle_bank_convert_caution(task: ExternalTask) -> TaskResult:
	"""Topic: bank-convert-caution (convert blocked caution into actual charge)"""
	logger.info("Executing SOAP Convert Caution to Charge")

	token		= task.get_variable(CAMUNDA_BANK_TOKEN)
	soap_body	= get_soap_body(
		f"""<convertCaution>
			<token>{token}</token>
		</convertCaution>""")
	
	try:
		response = soap_request(URL_BANK_WSDL, soap_body)

		if response.status_code == 200:
			root = ET.fromstring(response.content)
			status_element = root.find(".//status")
			
			if status_element is not None:
				status = status_element.text
				logger.info("Bank Convert Caution Status: %s", status)
				
				return task.complete({CAMUNDA_CONVERT_CAUTION_STATUS: status})
			else:
				return task.failure("Parse Error", "Could not find <status> in SOAP response", 0, 0)
		else:
			return task.failure("SOAP HTTP Error", f"Code {response.status_code}", 0, 0)
	except requests.exceptions.Timeout:
		logger.error("Bank service timed out!")
		return task.failure(
			error_message="Bank Service Timeout", 
			error_details="The bank service took more than 10 seconds to respond.",
			max_retries=REQUEST_MAX_RETRIES, 
			retry_timeout=REQUEST_RETRY_DELAY_MS
		)
	except Exception as e:
		logger.error("SOAP Error in Convert Caution: %s", e)
		return task.failure(error_message="Convert Caution Failed", error_details=str(e), max_retries=0, retry_timeout=0)



# =====================================================================
# STATION SERVICES (REST)
# =====================================================================

def handle_station_unlock(task: ExternalTask) -> TaskResult:
	"""Topic: station-unlock (unlock vehicle)"""
	vehicle_id = task.get_variable("vehicleId")
	logger.info("Sending REST request to Station to unlock %s", vehicle_id)
	
	try:
		# Example REST call
		# response = requests.post(f"{STATION_BASE_URL}/vehicle/unlock", json={"id": vehicle_id})
		# response.raise_for_status()
		
		return task.complete({"vehicleUnlocked": True})
	except Exception as e:
		logger.error("Station Unlock Failed: %s", e)
		return task.failure(error_message="Station Unlock Failed", error_details=str(e), max_retries=0, retry_timeout=0)


def handle_station_lock(task: ExternalTask) -> TaskResult:
	"""Topic: station-lock (lock vehicle)"""
	vehicle_id = task.get_variable("vehicleId")
	logger.info("Sending REST request to Station to lock %s", vehicle_id)
	
	# Simulate success
	return task.complete({"vehicleLocked": True})



# =====================================================================
# FLEET MANAGEMENT SERVICES (REST)
# =====================================================================

def handle_fleet_track_info(task: ExternalTask) -> TaskResult:
	"""Topic: fleet-track-info (get vehicle tracking info)"""
	vehicle_id = task.get_variable("vehicleId")
	logger.info("Fetching tracking info for %s from Fleet Service", vehicle_id)
	
	# Simulate API call to Fleet Management to get tracking info...
	# response = requests.get(f"{FLEET_BASE_URL}/vehicle/track-status", params={"id": vehicle_id})
	# data = response.json()
	
	# Simulated response
	#data = {
	#	"location": "POINT(45.4642 9.1900)", # Milan coordinates as example
	#	"speed": 25, # km/h
	#	"status": "moving"
	#}
	data = {}
	
	return task.complete({"trackingInfo": data})

def handle_fleet_track_start(task: ExternalTask) -> TaskResult:
	"""Topic: fleet-track-start (start vehicle tracking)"""
	logger.info("Starting fleet tracking via REST")
	return task.complete({"trackingStarted": True})

def handle_fleet_track_stop(task: ExternalTask) -> TaskResult:
	"""Topic: fleet-track-stop (stop vehicle tracking)"""
	logger.info("Stopping fleet tracking via REST")
	return task.complete({"trackingStopped": True})

def handle_fleet_fetch_battery(task: ExternalTask) -> TaskResult:
	"""Topic: fleet-fetch-battery"""
	logger.info("Fetching battery status from Fleet Service")
	# Simulate returning a battery percentage
	simulated_battery = 10 # Let's pretend it's 10% to trigger the penalty!
	return task.complete({"batteryLevel": simulated_battery})



# =====================================================================
# INTERNAL BUSINESS LOGIC (Calculations)
# =====================================================================

def handle_reserve_vehicle(task: ExternalTask) -> TaskResult:
	"""Topic: fleet-reserve"""
	vehicle_id = task.get_variable("vehicleId")
	logger.info("Reserving vehicle %s in ACME Fleet Management...", vehicle_id)
	
	# ACME Backend generates the secure, trusted timestamp
	trusted_now = datetime.now(timezone.utc).isoformat()
	
	# Simulate API call to Fleet Management to mark it as reserved...
	# requests.post(f"{FLEET_BASE_URL}/vehicle/reserve", json={"id": vehicle_id})
	
	# Save the trusted time into the Camunda process
	logger.info("Reservation time securely set to: %s", {trusted_now})
	return task.complete({"reserveTime": trusted_now})

def handle_check_cancellation_delay(task: ExternalTask) -> TaskResult:
	logger.info("Checking cancellation delay...")

	# Get the 'reserveTime' variable from Camunda
	# Camunda usually sends dates as ISO 8601 strings (e.g., "2023-10-27T10:00:00.000+0200")
	reserve_time_raw = task.get_variable("reserveTime")

	if not reserve_time_raw:
		logger.error("reserveTime not found in process variables!")
		return task.failure("Variable Missing", "reserveTime is required for this calculation", 0, 0)

	try:
		# Convert ISO string to Python datetime object
		# Note: We replace 'Z' with UTC offset to help Python's fromisoformat
		clean_time = reserve_time_raw.replace('Z', '+00:00')
		# If Camunda uses the format 2023-10-27T10:00:00.000+0200, we handle it:
		if "." in clean_time and "+" in clean_time.split(".")[-1]:
			# removing milliseconds for simpler parsing if necessary
			pass 
		
		reserve_datetime = datetime.fromisoformat(clean_time)
		now = datetime.now(reserve_datetime.tzinfo) # Use same timezone as input

		# Calculate the difference in minutes
		diff = now - reserve_datetime
		diff_minutes = diff.total_seconds() / 60

		logger.info("Reservation was made at %s. Now is %s. Delay: %.2f min", reserve_datetime, now, diff_minutes)

		# Return 'cancelMinutes' back to Camunda
		return task.complete({"cancelMinutes": diff_minutes})

	except Exception as e:
		logger.error("Error calculating delay: %s", e)
		return task.failure("Calculation Error", str(e), 0, 0)


def handle_calculate_charge(task: ExternalTask) -> TaskResult:
	"""Topic: calculate-charge"""
	logger.info("Calculating final amount to charge...")
	
	# In a real app, you'd calculate time difference here.
	base_cost = 15.00 # Simulated base cost for the ride
	
	return task.complete({"baseAmount": base_cost, "finalAmountToCharge": base_cost})


def handle_add_penalty(task: ExternalTask) -> TaskResult:
	"""Topic: apply-penalty (add 10% penalty)"""
	logger.info("Applying 10% battery penalty")
	
	base_cost = task.get_variable("baseAmount") or 15.00
	penalty = base_cost * 0.10
	final_amount = base_cost + penalty
	
	return task.complete({"finalAmountToCharge": final_amount, "penaltyApplied": True})


def handle_rejection(task: ExternalTask) -> TaskResult:
	"""Topic: notify-rejection (rental rejected)"""
	logger.warning("RENTAL REJECTED! Notifying systems...")
	return task.complete({})

