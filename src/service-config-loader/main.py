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



# =====================================================================
# WORKER STARTUP
# =====================================================================

def task_dispatcher(task: ExternalTask) -> TaskResult:
    topic = task.get_topic_name()
    
    if topic == "bank-preauth":
        return handle_bank_preauth(task)
    elif topic == "station-unlock":
        return handle_station_unlock(task)
    # ADD YOUR OTHER TOPICS HERE LATER:
    # elif topic == "fleet-reserve":
    #     return handle_reserve_vehicle(task)
    else:
        logger.warning(f"Unknown topic: {topic}")
        return task.failure("Unknown Topic", f"No handler for {topic}", 0, 0)



if __name__ == '__main__':
    logger.info("Waiting for Camunda to start...")
    time.sleep(10) # Wait for Camunda to fully boot up
    
    logger.info("Starting Workers... connecting to %s", CAMUNDA_URL)


    # Initialize the Worker
    worker = ExternalTaskWorker(worker_id="acme_python_worker", base_url=CAMUNDA_URL)

    topics_to_listen =[
        "bank-preauth",
        "bank-charge",
        "bank-unlock-caution",
        "bank-convert-caution",
        "station-unlock",
        "station-lock",
        "fleet-track-start",
        "fleet-fetch-battery",
        "acme-reserve",
        "acme-cancellation-delay",
        "acme-calculate-charge",
        "acme-apply-penalty",
        "acme-notify-rejection"

    ]

    logger.info("Subscribing to topics: %s", topics_to_listen)


    worker.subscribe(topics_to_listen, task_dispatcher)

    
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
    