import threading
import time
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

from server import run_server
from tasks_bank import (
	handle_bank_preauth,
	handle_bank_charge,
	handle_bank_unlock_caution,
	handle_bank_convert_caution
)
from tasks_stations import (
	handle_station_unlock,
	handle_station_lock
)
from tasks_fleet import (
	handle_fleet_track_info,
	handle_fleet_track_start,
	handle_fleet_track_stop,
	handle_fleet_fetch_battery
)
from tasks_acme import (
	handle_reserve_vehicle,
	handle_check_cancellation_delay,
	handle_calculate_charge,
	handle_add_penalty,
	handle_rejection
)
from get_env import config



# BPMN Topic Names -> Python Functions
TOPIC_MAP = {
	config.TOPIC_BANK_PREAUTH				: handle_bank_preauth,
	config.TOPIC_BANK_CHARGE				: handle_bank_charge,
	config.TOPIC_BANK_UNLOCK_CAUTION		: handle_bank_unlock_caution,
	config.TOPIC_BANK_CONVERT_CAUTION		: handle_bank_convert_caution,
	config.TOPIC_STATION_UNLOCK				: handle_station_unlock,
	config.TOPIC_STATION_LOCK				: handle_station_lock,
	config.TOPIC_FLEET_TRACK_INFO			: handle_fleet_track_info,
	config.TOPIC_FLEET_TRACK_START			: handle_fleet_track_start,
	config.TOPIC_FLEET_TRACK_STOP			: handle_fleet_track_stop,
	config.TOPIC_FLEET_FETCH_BATTERY		: handle_fleet_fetch_battery,
	config.TOPIC_ACME_RESERVE				: handle_reserve_vehicle,
	config.TOPIC_ACME_CANCELLATION_DELAY	: handle_check_cancellation_delay,
	config.TOPIC_ACME_CALCULATE_CHARGE		: handle_calculate_charge,
	config.TOPIC_ACME_APPLY_PENALTY			: handle_add_penalty,
	config.TOPIC_ACME_NOTIFY_REJECTION		: handle_rejection
}


# =====================================================================
# WORKER STARTUP
# =====================================================================

def task_dispatcher(task: ExternalTask) -> TaskResult:
	topic = task.get_topic_name()
	handler = TOPIC_MAP.get(topic)
	
	if handler:
		return handler(task)
	
	config.logger.error("No handler found for topic: %s", topic)
	return task.failure("Topic Error", f"No handler for {topic}", 0, 0)


if __name__ == '__main__':
	# Start (debugging) server, in a separate background thread.
	# Setting daemon=True ensures the thread dies when the main program stops
	threading.Thread(target=run_server, daemon=True).start()
	
	config.logger.info("Waiting for Camunda to start...")
	time.sleep(10)	# Wait for Camunda to fully boot up
	
	config.logger.info("Starting Workers... connecting to %s", config.URL_CAMUNDA)


	# Initialize the Worker
	worker = ExternalTaskWorker(worker_id="acme_python_worker", base_url=config.URL_CAMUNDA)


	config.logger.info("Subscribing to topics: %s", list(TOPIC_MAP.keys()))


	# Subscribe to the topics defined in the BPMN
	worker.subscribe(list(TOPIC_MAP.keys()), task_dispatcher)

	