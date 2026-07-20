import logging
import requests
from camunda.external_task.external_task import ExternalTask, TaskResult

from db import DATABASE, Vehicle
from get_env import config
from util import (
	REQUEST_TIMEOUT_SECONDS,
	perform_request,
)


logger = logging.getLogger(__name__)



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

	if station_id is None:
		config.logger.error("Station ID not provided for vehicle %s!", vehicle_id)
		return task.failure("Station ID Not Provided", f"Station ID not provided for vehicle {vehicle_id}.", 0, 0)

	station_url = config.STATION_ID_URL_MAP.get(station_id)
	if station_url is None:
		config.logger.error("No URL configured for station %s!", station_id)
		return task.failure("Station URL Not Configured", f"No URL configured for station {station_id}.", 0, 0)


	def func_success(
		task		: ExternalTask,
		# pylint: disable=W0613
		response	: requests.Response
	) -> TaskResult:
		DATABASE.update_vehicle( Vehicle(
			vehicle_id		= vehicle_id,
			status			=
				Vehicle.Status.CHARGING if vehicle.battery_perc < config.CAMUNDA_BATTERY_LOW_THRESHOLD
				else Vehicle.Status.AVAILABLE,
			reserved_by		= vehicle.reserved_by,
			rented_by		= vehicle.rented_by,
			current_station	= station_id,
			battery_perc	= vehicle.battery_perc
		))
		config.logger.info("Vehicle %s locked successfully at station %s!", vehicle_id, station_id)
		return task.complete({config.CAMUNDA_STATUS_VEHICLE_LOCKED: True})

	# set to Maintenance
	def func_on_error(
		task		: ExternalTask,
		response	: requests.Response
	) -> None:
		DATABASE.update_vehicle( Vehicle(
			vehicle_id		= vehicle_id,
			status			= Vehicle.Status.MAINTENANCE,
			reserved_by		= None,
			rented_by		= None,
			current_station	= None,		# not locked anywhere
			battery_perc	= vehicle.battery_perc
		))

	return perform_request(
		task,
		func_request	= lambda: requests.post(station_url + config.EP_STATION_LOCK, json={
				"vehicleId": vehicle_id
			}, timeout	= REQUEST_TIMEOUT_SECONDS),
		func_success	= func_success,
		action_name		= "Lock Vehicle at Station",
		status_var		= config.CAMUNDA_STATUS_VEHICLE_LOCKED,
		func_on_error	= func_on_error
	)



def handle_station_unlock(task: ExternalTask) -> TaskResult:
	"""Topic: station-unlock (unlock vehicle)"""

	vehicle_id	= task.get_variable(config.CAMUNDA_VEHICLE_ID)

	vehicle	= DATABASE.get_vehicle(vehicle_id)
	if vehicle is None:
		config.logger.error("Vehicle %s not found!", vehicle_id)
		return task.failure("Vehicle Not Found", f"Vehicle {vehicle_id} not found.", 0, 0)

	station_id = vehicle.current_station
	if station_id is None:
		config.logger.error("Vehicle %s is not at any station!", vehicle_id)
		return task.failure("Vehicle Not at Station", f"Vehicle {vehicle_id} is not at any station.", 0, 0)

	station_url = config.STATION_ID_URL_MAP.get(station_id)
	if station_url is None:
		config.logger.error("No URL configured for station %s!", station_id)
		return task.failure("Station URL Not Configured", f"No URL configured for station {station_id}.", 0, 0)


	def func_success(
		task		: ExternalTask,
		# pylint: disable=W0613
		response	: requests.Response
	) -> TaskResult:
		DATABASE.update_vehicle( Vehicle(
			vehicle_id		= vehicle_id,
			status			= Vehicle.Status.RENTED,
			reserved_by		= None,
			rented_by		= vehicle.rented_by,
			current_station	= None,
			battery_perc	= vehicle.battery_perc
		))
		config.logger.info("Vehicle %s unlocked successfully at station %s!", vehicle_id, station_id)
		return task.complete({config.CAMUNDA_STATUS_VEHICLE_LOCKED: True})

	# set to Maintenance
	def func_on_error(
		task		: ExternalTask,
		response	: requests.Response
	) -> None:
		DATABASE.update_vehicle( Vehicle(
			vehicle_id		= vehicle_id,
			status			= Vehicle.Status.MAINTENANCE,
			reserved_by		= None,
			rented_by		= None,
			current_station	= vehicle.current_station,
			battery_perc	= vehicle.battery_perc
		))

	return perform_request(
		task,
		func_request	= lambda: requests.post(station_url + config.EP_STATION_UNLOCK, json={
				"vehicleId": vehicle_id
			}, timeout	= REQUEST_TIMEOUT_SECONDS),
		func_success	= func_success,
		action_name		= "Unlock Vehicle at Station",
		status_var		= config.CAMUNDA_STATUS_VEHICLE_UNLOCKED,
		func_on_error	= func_on_error
	)

