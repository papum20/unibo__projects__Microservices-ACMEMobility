import requests
from camunda.external_task.external_task import ExternalTask, TaskResult

from db import DATABASE, Vehicle
from get_env import config
from util import (
	REQUEST_TIMEOUT_SECONDS,
	perform_request,
	func_success_status
)



# =====================================================================
# FLEET MANAGEMENT SERVICES (REST)
# =====================================================================

def handle_fleet_track_info(task: ExternalTask) -> TaskResult:
	"""Topic: fleet-track-info (get vehicle tracking info)"""
	vehicle_id	= task.get_variable(config.CAMUNDA_VEHICLE_ID)
	vehicle		= DATABASE.get_vehicle(vehicle_id)

	if vehicle is None:
		config.logger.error("Vehicle %s not found!", vehicle_id)
		return task.failure("Vehicle Not Found", f"Vehicle {vehicle_id} not found.", 0, 0)

	def func_success(
		task		: ExternalTask,
		# pylint: disable=W0613
		response	: requests.Response
	) -> TaskResult:
		data = response.json()
		config.logger.info("Received tracking info for %s: %s", vehicle_id, data)
		return task.complete({config.CAMUNDA_TRACKING_INFO: data})

	return perform_request(
		task,
		func_request	= lambda: requests.get(config.URL_FLEET_BASE + config.EP_FLEET_POSITION.format(vehicleId=vehicle_id),
			params		= {
				"vehicleId": vehicle_id
			}, timeout	= REQUEST_TIMEOUT_SECONDS),
		action_name		= "Fetch Fleet Tracking Info for " + str(vehicle_id),
		status_var		= config.CAMUNDA_TRACKING_INFO,
		func_success	= func_success
	)


def handle_fleet_track_start(task: ExternalTask) -> TaskResult:
	"""Topic: fleet-track-start (start vehicle tracking)"""
	vehicle_id	= task.get_variable(config.CAMUNDA_VEHICLE_ID)
	vehicle		= DATABASE.get_vehicle(vehicle_id)

	if vehicle is None:
		config.logger.error("Vehicle %s not found!", vehicle_id)
		return task.failure("Vehicle Not Found", f"Vehicle {vehicle_id} not found.", 0, 0)

	if vehicle.status != Vehicle.Status.AVAILABLE:
		config.logger.error("Vehicle %s is not available for tracking! Current status: %s", vehicle_id, vehicle.status.value)
		return task.failure("Unavailable", f"Vehicle status is {vehicle.status.value}", 0, 0)

	DATABASE.update_vehicle( Vehicle(
		vehicle_id		= vehicle_id,
		status			= Vehicle.Status.RENTED,
		reserved_by		= vehicle.reserved_by,
		rented_by		= task.get_variable(config.CAMUNDA_USER_ID),
		current_station	= None,
		battery_perc	= vehicle.battery_perc
	))

	return perform_request(
		task,
		func_request	= lambda: requests.post(config.URL_FLEET_BASE + config.EP_FLEET_TRACK_START, json={
				"vehicleId"	: vehicle_id,
				"userId"	: task.get_variable(config.CAMUNDA_USER_ID)
			}, timeout	= REQUEST_TIMEOUT_SECONDS),
		func_success	= func_success_status(config.CAMUNDA_STATUS_TRACKING_STARTED),
		action_name		= "Start Fleet Tracking",
		status_var		= config.CAMUNDA_STATUS_TRACKING_STARTED
	)
	

def handle_fleet_track_stop(task: ExternalTask) -> TaskResult:
	"""Topic: fleet-track-stop (stop vehicle tracking)"""
	vehicle_id	= task.get_variable(config.CAMUNDA_VEHICLE_ID)
	vehicle		= DATABASE.get_vehicle(vehicle_id)

	if vehicle is None:
		config.logger.error("Vehicle %s not found!", vehicle_id)
		return task.failure("Vehicle Not Found", f"Vehicle {vehicle_id} not found.", 0, 0)

	return perform_request(
		task,
		func_request	= lambda: requests.post(config.URL_FLEET_BASE + config.EP_FLEET_TRACK_STOP, json={
				"vehicleId": vehicle_id,
				"userId": task.get_variable(config.CAMUNDA_USER_ID)
			}, timeout	= REQUEST_TIMEOUT_SECONDS),
		func_success	= func_success_status(config.CAMUNDA_STATUS_TRACKING_STOPPED),
		action_name		= "Stop Fleet Tracking",
		status_var		= config.CAMUNDA_STATUS_TRACKING_STOPPED
	)


def handle_fleet_fetch_battery(task: ExternalTask) -> TaskResult:
	"""Topic: fleet-fetch-battery"""
	vehicle_id	= task.get_variable(config.CAMUNDA_VEHICLE_ID)
	vehicle		= DATABASE.get_vehicle(vehicle_id)

	if vehicle is None:
		config.logger.error("Vehicle %s not found!", vehicle_id)
		return task.failure("Vehicle Not Found", f"Vehicle {vehicle_id} not found.", 0, 0)

	def func_success(
		task		: ExternalTask,
		# pylint: disable=W0613
		response	: requests.Response
	) -> TaskResult:
		data = response.json()
		battery_level = data.get(config.CAMUNDA_BATTERY_LEVEL)
		config.logger.info("Received battery level for %s: %s%%", vehicle_id, battery_level)
		DATABASE.update_vehicle( Vehicle(
			vehicle_id		= vehicle_id,
			status			= vehicle.status,
			reserved_by		= vehicle.reserved_by,
			rented_by		= vehicle.rented_by,
			current_station	= vehicle.current_station,
			battery_perc	= battery_level
		))
		return task.complete({config.CAMUNDA_BATTERY_LEVEL: battery_level})
	
	return perform_request(
		task,
		func_request	= lambda: requests.get(config.URL_FLEET_BASE + config.EP_FLEET_BATTERY.format(vehicleId=vehicle_id),
			params		= {
				"vehicleId": vehicle_id
			}, timeout	= REQUEST_TIMEOUT_SECONDS),
		action_name		= "Fetch Fleet Battery Level for " + str(vehicle_id),
		status_var		= config.CAMUNDA_BATTERY_LEVEL,
		func_success	= func_success
	)

