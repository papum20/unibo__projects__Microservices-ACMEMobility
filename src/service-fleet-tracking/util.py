from get_env import get_env_or_exit


VEHICLE_PREFIX      = get_env_or_exit('VEHICLE_PREFIX')
URL_VEHICLE_PARAM   = get_env_or_exit('URL_VEHICLE_PARAM')


def get_vehicle_url(vehicle_id: str) -> str:
	vehicle_suffix = vehicle_id.rsplit(f'{VEHICLE_PREFIX}-', 1)[-1]
	return URL_VEHICLE_PARAM.replace("{vehicleSuffix}", vehicle_suffix)
