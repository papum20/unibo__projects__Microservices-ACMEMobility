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

# Read Configuration from Docker Environment (Base URLs)
CAMUNDA_URL			= get_env_or_exit('URL_CAMUNDA')
BANK_BASE_URL		= get_env_or_exit('URL_BANK')
STATION_BASE_URL	= get_env_or_exit('URL_STATION')
BANK_CAUTION		= get_env_or_exit('BANK_CAUTION')

# BPMN Topic Names -> Python Functions
TOPIC_MAP = {
	"bank-preauth"				: handle_bank_preauth,
	"bank-charge"				: handle_bank_charge,
	"bank-unlock-caution"		: handle_bank_unlock_caution,
	"bank-convert-caution"		: handle_bank_charge,  # reuse charge logic
	"station-unlock"			: handle_station_unlock,
	"station-lock"				: handle_station_lock,
	"fleet-track-start"			: handle_fleet_track_start,
	"fleet-track-stop"			: handle_fleet_track_stop,
	"fleet-fetch-battery"		: handle_fleet_fetch_battery,
	"acme-reserve"				: handle_reserve_vehicle,
	"acme-cancellation-delay"	: handle_check_cancellation_delay,
	"acme-calculate-charge"		: handle_calculate_charge,
	"acme-apply-penalty"		: handle_add_penalty,
	"acme-notify-rejection"		: handle_rejection
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
	