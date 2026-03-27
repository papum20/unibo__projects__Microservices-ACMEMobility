import time
import logging
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

from service_tasks import (
	handle_bank_preauth,
	handle_bank_charge,
	handle_bank_unlock_caution,
	handle_station_unlock,
	handle_station_lock,
	handle_fleet_track_info,
	handle_fleet_track_start,
	handle_fleet_track_stop,
	handle_fleet_fetch_battery,
	handle_reserve_vehicle,
	handle_check_cancellation_delay,
	handle_calculate_charge,
	handle_add_penalty,
	handle_rejection
)
from util import get_env_or_exit



# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read Configuration from Docker Environment
CAMUNDA_URL			= get_env_or_exit('URL_CAMUNDA')
BANK_BASE_URL		= get_env_or_exit('URL_BANK')
STATION_BASE_URL	= get_env_or_exit('URL_STATION')
BANK_CAUTION		= get_env_or_exit('BANK_CAUTION')

TOPIC_BANK_PREAUTH				= get_env_or_exit('TOPIC_BANK_PREAUTH')
TOPIC_BANK_CHARGE				= get_env_or_exit('TOPIC_BANK_CHARGE')
TOPIC_BANK_CONVERT_CAUTION		= get_env_or_exit('TOPIC_BANK_CONVERT_CAUTION')
TOPIC_BANK_UNLOCK_CAUTION		= get_env_or_exit('TOPIC_BANK_UNLOCK_CAUTION')
TOPIC_STATION_LOCK				= get_env_or_exit('TOPIC_STATION_LOCK')
TOPIC_STATION_UNLOCK			= get_env_or_exit('TOPIC_STATION_UNLOCK')
TOPIC_FLEET_TRACK_INFO			= get_env_or_exit('TOPIC_FLEET_TRACK_INFO')
TOPIC_FLEET_TRACK_START			= get_env_or_exit('TOPIC_FLEET_TRACK_START')
TOPIC_FLEET_TRACK_STOP			= get_env_or_exit('TOPIC_FLEET_TRACK_STOP')
TOPIC_FLEET_FETCH_BATTERY		= get_env_or_exit('TOPIC_FLEET_FETCH_BATTERY')
TOPIC_ACME_APPLY_PENALTY		= get_env_or_exit('TOPIC_ACME_APPLY_PENALTY')
TOPIC_ACME_CALCULATE_CHARGE		= get_env_or_exit('TOPIC_ACME_CALCULATE_CHARGE')
TOPIC_ACME_CANCELLATION_DELAY	= get_env_or_exit('TOPIC_ACME_CANCELLATION_DELAY')
TOPIC_ACME_NOTIFY_REJECTION		= get_env_or_exit('TOPIC_ACME_NOTIFY_REJECTION')
TOPIC_ACME_RESERVE				= get_env_or_exit('TOPIC_ACME_RESERVE')

# BPMN Topic Names -> Python Functions
TOPIC_MAP = {
	TOPIC_BANK_PREAUTH				: handle_bank_preauth,
	TOPIC_BANK_CHARGE				: handle_bank_charge,
	TOPIC_BANK_UNLOCK_CAUTION		: handle_bank_unlock_caution,
	TOPIC_BANK_CONVERT_CAUTION		: handle_bank_charge,  # reuse charge logic
	TOPIC_STATION_UNLOCK			: handle_station_unlock,
	TOPIC_STATION_LOCK				: handle_station_lock,
	TOPIC_FLEET_TRACK_INFO			: handle_fleet_track_info,
	TOPIC_FLEET_TRACK_START			: handle_fleet_track_start,
	TOPIC_FLEET_TRACK_STOP			: handle_fleet_track_stop,
	TOPIC_FLEET_FETCH_BATTERY		: handle_fleet_fetch_battery,
	TOPIC_ACME_RESERVE				: handle_reserve_vehicle,
	TOPIC_ACME_CANCELLATION_DELAY	: handle_check_cancellation_delay,
	TOPIC_ACME_CALCULATE_CHARGE		: handle_calculate_charge,
	TOPIC_ACME_APPLY_PENALTY		: handle_add_penalty,
	TOPIC_ACME_NOTIFY_REJECTION		: handle_rejection
}


# =====================================================================
# WORKER STARTUP
# =====================================================================

def task_dispatcher(task: ExternalTask) -> TaskResult:
	topic = task.get_topic_name()
	handler = TOPIC_MAP.get(topic)
	
	if handler:
		return handler(task)
	
	logger.error("No handler found for topic: %s", topic)
	return task.failure("Topic Error", f"No handler for {topic}", 0, 0)


if __name__ == '__main__':
	logger.info("Waiting for Camunda to start...")
	time.sleep(10)	# Wait for Camunda to fully boot up
	
	logger.info("Starting Workers... connecting to %s", CAMUNDA_URL)


	# Initialize the Worker
	worker = ExternalTaskWorker(worker_id="acme_python_worker", base_url=CAMUNDA_URL)


	logger.info("Subscribing to topics: %s", list(TOPIC_MAP.keys()))


	worker.subscribe(list(TOPIC_MAP.keys()), task_dispatcher)

	
	# Subscribe to the topics defined in the BPMN

	#worker.subscribe("config-loader", handle_config)
	
	# Bank
	#worker.subscribe("bank-preauth", handle_bank_preauth)
	#worker.subscribe("bank-charge", handle_bank_charge)                     # type: ignore
	#worker.subscribe("bank-unlock-caution", handle_bank_unlock_caution)
	#worker.subscribe("bank-convert-caution", handle_bank_charge)            # reuse charge logic
	#
	## Station
	#worker.subscribe("station-unlock", handle_station_unlock)
	#worker.subscribe("station-lock", handle_station_lock)
	#
	## Fleet
	#worker.subscribe("fleet-track-start", handle_fleet_track_start)
	#worker.subscribe("fleet-fetch-battery", handle_fleet_fetch_battery)
	#
	## Internal Logic
	#worker.subscribe("acme-reserve", handle_reserve_vehicle)
	#worker.subscribe("acme-cancellation-delay", handle_check_cancellation_delay)
	#worker.subscribe("acme-calculate-charge", handle_calculate_charge)
	#worker.subscribe("acme-apply-penalty", handle_add_penalty)
	#worker.subscribe("acme-notify-rejection", handle_rejection)
	