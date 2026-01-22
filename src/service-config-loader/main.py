import os
import time
import logging
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Read Configuration from Docker Environment (Base URLs)
CAMUNDA_URL			= os.environ.get('URL_CAMUNDA', 'http://localhost:8080/engine-rest')
BANK_BASE_URL		= os.environ.get('URL_BANK', 'http://bank-service:8000')
STATION_BASE_URL	= os.environ.get('URL_STATION', 'http://stations-service:5000')
BANK_CAUTION		= os.environ.get('BANK_CAUTION', 10)

def handle_config(task: ExternalTask) -> TaskResult:
    logger.info(f"Received config request for Process Instance: {task.process_instance_id}")

    # 2. Define Endpoints (API Paths)
    # These are the specific paths for your Jolie/Python services
    # You can change them here if your API signature changes
    
    # Bank Endpoints
    ep_bank_preauth = "/preAuth"
    ep_bank_charge  = "/charge"
    ep_bank_unlock  = "/unlock"

    # Station Endpoints
    ep_station_unlock = "/vehicle/unlock"
    ep_station_lock   = "/vehicle/lock"
    
    # Fleet Endpoints (Assuming standard REST paths)
    ep_fleet_track_start	= "/vehicle/track-start"
    ep_fleet_track_status   = "/vehicle/track-status"
    ep_fleet_battery        = "/vehicle/battery"

    # 3. Pack everything into variables for Camunda
    # We send both Base URLs and Endpoints separately
    config_variables = {
        # Base URLs
        "urlBank": BANK_BASE_URL,
        "urlStation": STATION_BASE_URL,

        # Bank
        "epBankPreAuth": ep_bank_preauth,
        "epBankCharge": ep_bank_charge,
        "epBankUnlock": ep_bank_unlock,
        "valBankCaution": BANK_CAUTION,

        # Station
        "epStationUnlock": ep_station_unlock,
        "epStationLock": ep_station_lock,
        
        # Fleet (Example)
        "epFleetTrackStart": ep_fleet_track_start,
        "epFleetTrackStatus": ep_fleet_track_status,
		"epFleetBattery": ep_fleet_battery
    }

    logger.info(f"Injecting configuration: {config_variables}")

    # 4. Complete the task and inject variables into the Process Scope
    return task.complete(global_variables=config_variables)

if __name__ == '__main__':
    logger.info("Waiting for Camunda to start...")
    time.sleep(10) # Wait for Camunda to fully boot up
    
    logger.info(f"Starting Config Loader Worker... connecting to {CAMUNDA_URL}")
    
    # Initialize the Worker
    worker = ExternalTaskWorker(worker_id="acme_config_loader_1", base_url=CAMUNDA_URL)
    
    # Subscribe to the topic defined in your BPMN
    worker.subscribe("config-loader", handle_config)