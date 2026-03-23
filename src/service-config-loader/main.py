import os
import time
import logging
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

from service_tasks import (
    handle_config,
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



# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Read Configuration from Docker Environment (Base URLs)
CAMUNDA_URL			= os.environ.get('URL_CAMUNDA', 'http://localhost:8080/engine-rest')
BANK_BASE_URL		= os.environ.get('URL_BANK', 'http://bank-service:8000')
STATION_BASE_URL	= os.environ.get('URL_STATION', 'http://stations-service:5000')
BANK_CAUTION		= os.environ.get('BANK_CAUTION', 10)



# =====================================================================
# WORKER STARTUP
# =====================================================================


if __name__ == '__main__':
    logger.info("Waiting for Camunda to start...")
    time.sleep(10) # Wait for Camunda to fully boot up
    
    logger.info("Starting Workers... connecting to %s", CAMUNDA_URL)


    # Initialize the Worker
    worker = ExternalTaskWorker(worker_id="acme_python_worker", base_url=CAMUNDA_URL)

    
    # Subscribe to the topics defined in the BPMN

    #worker.subscribe("config-loader", handle_config)
    
    # Bank
    worker.subscribe("bank-preauth", handle_bank_preauth)
    worker.subscribe("bank-charge", handle_bank_charge)
    worker.subscribe("bank-unlock-caution", handle_bank_unlock_caution)
    worker.subscribe("bank-convert-caution", handle_bank_charge) # reuse charge logic
    
    # Station
    worker.subscribe("station-unlock", handle_station_unlock)
    worker.subscribe("station-lock", handle_station_lock)
    
    # Fleet
    worker.subscribe("fleet-track-start", handle_fleet_track_start)
    worker.subscribe("fleet-fetch-battery", handle_fleet_fetch_battery)
    
    # Internal Logic
    worker.subscribe("acme-reserve", handle_reserve_vehicle)
    worker.subscribe("acme-cancellation-delay", handle_check_cancellation_delay)
    worker.subscribe("acme-calculate-charge", handle_calculate_charge)
    worker.subscribe("acme-apply-penalty", handle_add_penalty)
    worker.subscribe("acme-notify-rejection", handle_rejection)
    
    # Remove config-loader as we no longer need it!
    # (If you left the config-loader box in your BPMN, you can just delete it from the diagram).