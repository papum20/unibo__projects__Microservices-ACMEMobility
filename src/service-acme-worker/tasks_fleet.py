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


