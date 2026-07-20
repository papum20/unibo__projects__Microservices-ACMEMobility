from datetime import datetime, timezone
import logging
from camunda.external_task.external_task import ExternalTask, TaskResult

from db import DATABASE, Vehicle
from get_env import config



# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# =====================================================================
# INTERNAL BUSINESS LOGIC (Calculations)
# =====================================================================

def handle_reserve_vehicle(task: ExternalTask) -> TaskResult:
	"""Topic: fleet-reserve"""
	vehicle_id	= task.get_variable("vehicleId")
	vehicle		= DATABASE.get_vehicle(vehicle_id)
	logger.info("Reserving vehicle %s in ACME Fleet Management...", vehicle_id)

	if vehicle is None:
		config.logger.error("Vehicle %s not found!", vehicle_id)
		return task.failure("Vehicle Not Found", f"Vehicle {vehicle_id} not found.", 0, 0)

	# ACME Backend generates the secure, trusted timestamp
	trusted_now = datetime.now(timezone.utc).isoformat()
	
	# Save the trusted time into the Camunda process
	logger.info("Reservation time securely set to: %s", {trusted_now})
	return task.complete({config.CAMUNDA_RESERVE_TIME: trusted_now})

def handle_check_cancellation_delay(task: ExternalTask) -> TaskResult:
	logger.info("Checking cancellation delay...")

	# Get the 'reserveTime' variable from Camunda
	# Camunda usually sends dates as ISO 8601 strings (e.g., "2023-10-27T10:00:00.000+0200")
	reserve_time_raw = task.get_variable(config.CAMUNDA_RESERVE_TIME)

	if not reserve_time_raw:
		logger.error("%s not found in process variables!", config.CAMUNDA_RESERVE_TIME)
		return task.failure("Variable Missing", f"{config.CAMUNDA_RESERVE_TIME} is required for this calculation", 0, 0)

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

