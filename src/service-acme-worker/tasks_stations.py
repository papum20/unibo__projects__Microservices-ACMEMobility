from datetime import datetime, timezone
import logging
import requests
import xml.etree.ElementTree as ET
from camunda.external_task.external_task import ExternalTask, TaskResult

from get_env import envConfig



# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



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

