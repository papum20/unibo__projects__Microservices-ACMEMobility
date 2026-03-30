from datetime import datetime, timezone
import logging
from camunda.external_task.external_task import ExternalTask, TaskResult

from get_env import config



# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



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
		"urlBank": config.URL_BANK_BASE,
		"urlStation": config.URL_STATION_BASE,

		# Bank
		"epBankPreAuth": ep_bank_preauth,
		"epBankCharge": ep_bank_charge,
		"epBankUnlock": ep_bank_unlock,
		"valBankCaution": config.BANK_CAUTION,

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

