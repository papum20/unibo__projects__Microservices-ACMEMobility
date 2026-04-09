import requests
from camunda.external_task.external_task import ExternalTask, TaskResult

from db import DATABASE, Vehicle
from get_env import config
from util import (
	REQUEST_TIMEOUT_SECONDS,
	perform_request,
)



# =====================================================================
# STATION SERVICES (REST)
# =====================================================================


def handle_station_lock(task: ExternalTask) -> TaskResult:
	"""Topic: station-lock (lock vehicle)"""

	station_id	= task.get_variable(config.CAMUNDA_STATION_ID)
	vehicle_id	= task.get_variable(config.CAMUNDA_VEHICLE_ID)

	vehicle	= DATABASE.get_vehicle(vehicle_id)
	if vehicle is None:
		config.logger.error("Vehicle %s not found!", vehicle_id)
		return task.failure("Vehicle Not Found", f"Vehicle {vehicle_id} not found.", 0, 0)

	def func_success(
		task		: ExternalTask,
		# pylint: disable=W0613
		response	: requests.Response
	) -> TaskResult:
		DATABASE.update_vehicle( Vehicle(
			vehicle_id		= vehicle_id,
			status			= Vehicle.Status.CHARGING,
			reserved_by		= vehicle.reserved_by,
			rented_by		= vehicle.rented_by,
			current_station	= station_id
		))
		config.logger.info("Vehicle %s locked successfully at station %s!", vehicle_id, station_id)
		return task.complete({config.CAMUNDA_STATUS_VEHICLE_LOCKED: True})

	return perform_request(
		task,
		func_request	= lambda: requests.post(config.URL_STATION_BASE + config.EP_STATION_LOCK, json={
				"vehicleId": vehicle_id,
				"stationId": station_id
			}, timeout	= REQUEST_TIMEOUT_SECONDS),
		func_success	= func_success,
		action_name		= "Lock Vehicle at Station",
		status_var		= config.CAMUNDA_STATUS_VEHICLE_LOCKED
	)


def handle_station_unlock(task: ExternalTask) -> TaskResult:
	"""Topic: station-unlock (unlock vehicle)"""

	vehicle_id	= task.get_variable(config.CAMUNDA_VEHICLE_ID)

	vehicle	= DATABASE.get_vehicle(vehicle_id)
	if vehicle is None:
		config.logger.error("Vehicle %s not found!", vehicle_id)
		return task.failure("Vehicle Not Found", f"Vehicle {vehicle_id} not found.", 0, 0)

	stationId = vehicle.current_station
	if stationId is None:
		config.logger.error("Vehicle %s is not at any station!", vehicle_id)
		return task.failure("Vehicle Not at Station", f"Vehicle {vehicle_id} is not at any station.", 0, 0)

	def func_success(
		task		: ExternalTask,
		# pylint: disable=W0613
		response	: requests.Response
	) -> TaskResult:
		DATABASE.update_vehicle( Vehicle(
			vehicle_id		= vehicle_id,
			status			= Vehicle.Status.AVAILABLE,
			reserved_by		= vehicle.reserved_by,
			rented_by		= vehicle.rented_by,
			current_station	= stationId
		))
		config.logger.info("Vehicle %s unlocked successfully at station %s!", vehicle_id, stationId)
		return task.complete({config.CAMUNDA_STATUS_VEHICLE_LOCKED: True})

	return perform_request(
		task,
		func_request	= lambda: requests.post(config.URL_STATION_BASE + config.EP_STATION_UNLOCK, json={
				"vehicleId": vehicle_id,
				"stationId": stationId
			}, timeout	= REQUEST_TIMEOUT_SECONDS),
		func_success	= func_success,
		action_name		= "Unlock Vehicle at Station",
		status_var		= config.CAMUNDA_STATUS_VEHICLE_UNLOCKED
	)

