import os
from datetime import datetime, timezone
import time
import logging
import requests
from zeep import Client, exceptions as zeep_exceptions
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION (Loaded directly from Environment) ---
CAMUNDA_URL         = os.environ.get('URL_CAMUNDA', 'http://camunda:8080/engine-rest')
BANK_WSDL_URL       = os.environ.get('URL_BANK_WSDL', 'http://bank-service:8000/bank?wsdl') # Jolie SOAP WSDL
STATION_BASE_URL    = os.environ.get('URL_STATION', 'http://stations-service:5000')
FLEET_BASE_URL      = os.environ.get('URL_FLEET', 'http://fleet-service:4000')
BANK_BASE_URL		= os.environ.get('URL_BANK', 'http://bank-service:8000')
STATION_BASE_URL	= os.environ.get('URL_STATION', 'http://stations-service:5000')

BANK_CAUTION        = int(os.environ.get('BANK_CAUTION', 10))



def handle_config(task: ExternalTask) -> TaskResult:
    logger.info("Received config request for Process Instance: %s", task.get_process_instance_id())

    # Define Endpoints (API Paths)
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

    logger.info("Injecting configuration: %s", config_variables)

    # 4. Complete the task and inject variables into the Process Scope
    return task.complete(global_variables=config_variables)



# =====================================================================
# BANK SERVICES (JOLIE - SOAP via Zeep)
# =====================================================================

def handle_bank_preauth(task: ExternalTask) -> TaskResult:
    """Topic: bank-preauth (block 10€ caution money)"""
    logger.info("Executing SOAP PreAuth for process %s", task.get_process_instance_id())
    try:
        # Initialize SOAP Client
        client = Client(wsdl=BANK_WSDL_URL)
        # Call the Jolie SOAP operation (assuming operation is named 'preAuthorize')
        response = client.service.preAuthorize(amount=BANK_CAUTION)
        
        # We save the bank token to Camunda so we can use it later
        return task.complete({"bankToken": response.token, "cautionBlocked": True})
    except Exception as e:
        logger.error("SOAP Error in PreAuth: %s", e)
        return task.failure(error_message="Bank PreAuth Failed", error_details=str(e), max_retries=0, retry_timeout=0)

def handle_bank_charge(task: ExternalTask) -> TaskResult:
    """Topic: bank-charge (charge user)"""
    logger.info("Executing SOAP Charge")
    # Get variables from Camunda context
    token = task.get_variable("bankToken")
    amount = task.get_variable("finalAmountToCharge") # Calculated in another task
    
    try:
        client = Client(wsdl=BANK_WSDL_URL)
        client.service.charge(token=token, amount=amount)
        return task.complete({"paymentStatus": "success"})
    except Exception as e:
        return task.failure(error_message="Charge Failed", error_details=str(e), max_retries=0, retry_timeout=0)

def handle_bank_unlock_caution(task: ExternalTask) -> TaskResult:
    """Topic: bank-unlock-caution"""
    logger.info("Executing SOAP Unlock Caution")
    token = task.get_variable("bankToken")
    try:
        client = Client(wsdl=BANK_WSDL_URL)
        client.service.unlockCaution(token=token)
        return task.complete({"cautionUnlocked": True})
    except Exception as e:
        return task.failure(error_message="Unlock Caution Failed", error_details=str(e), max_retries=0, retry_timeout=0)



# =====================================================================
# STATION SERVICES (REST)
# =====================================================================

def handle_station_unlock(task: ExternalTask) -> TaskResult:
    """Topic: station-unlock (unlock vehicle)"""
    vehicle_id = task.get_variable("vehicleId") or "V-123"
    logger.info("Sending REST request to Station to unlock %s", vehicle_id)
    
    try:
        # Example REST call
        # response = requests.post(f"{STATION_BASE_URL}/vehicle/unlock", json={"id": vehicle_id})
        # response.raise_for_status()
        
        return task.complete({"vehicleUnlocked": True})
    except Exception as e:
        return task.failure(error_message="Station Unlock Failed", error_details=str(e), max_retries=0, retry_timeout=0)

def handle_station_lock(task: ExternalTask) -> TaskResult:
    """Topic: station-lock (lock vehicle)"""
    vehicle_id = task.get_variable("vehicleId") or "V-123"
    logger.info("Sending REST request to Station to lock %s", vehicle_id)
    
    # Simulate success
    return task.complete({"vehicleLocked": True})



# =====================================================================
# FLEET MANAGEMENT SERVICES (REST)
# =====================================================================

def handle_fleet_track_start(task: ExternalTask) -> TaskResult:
    """Topic: fleet-track-start (start vehicle tracking)"""
    logger.info("Starting fleet tracking via REST")
    return task.complete({"trackingStarted": True})

def handle_fleet_fetch_battery(task: ExternalTask) -> TaskResult:
    """Topic: fleet-fetch-battery"""
    logger.info("Fetching battery status from Fleet Service")
    # Simulate returning a battery percentage
    simulated_battery = 10 # Let's pretend it's 10% to trigger the penalty!
    return task.complete({"batteryLevel": simulated_battery})



# =====================================================================
# INTERNAL BUSINESS LOGIC (Calculations)
# =====================================================================

def handle_reserve_vehicle(task: ExternalTask) -> TaskResult:
    """Topic: fleet-reserve"""
    vehicle_id = task.get_variable("vehicleId")
    logger.info("Reserving vehicle %s in ACME Fleet Management...", vehicle_id)
    
    # ACME Backend generates the secure, trusted timestamp
    trusted_now = datetime.now(timezone.utc).isoformat()
    
    # Simulate API call to Fleet Management to mark it as reserved...
    # requests.post(f"{FLEET_BASE_URL}/vehicle/reserve", json={"id": vehicle_id})
    
    # Save the trusted time into the Camunda process
    logger.info("Reservation time securely set to: %s", {trusted_now})
    return task.complete({"reserveTime": trusted_now})

def handle_check_cancellation_delay(task: ExternalTask) -> TaskResult:
    logger.info("Checking cancellation delay...")

    # Get the 'reserveTime' variable from Camunda
    # Camunda usually sends dates as ISO 8601 strings (e.g., "2023-10-27T10:00:00.000+0200")
    reserve_time_raw = task.get_variable("reserveTime")

    if not reserve_time_raw:
        logger.error("reserveTime not found in process variables!")
        return task.failure("Variable Missing", "reserveTime is required for this calculation", 0, 0)

    try:
        # Convert ISO string to Python datetime object
        # Note: We replace 'Z' with UTC offset to help Python's fromisoformat
        clean_time = reserve_time_raw.replace('Z', '+00:00')
        # If Camunda uses the format 2023-10-27T10:00:00.000+0200, we handle it:
        if "." in clean_time and "+" in clean_time.split(".")[-1]:
            # removing milliseconds for simpler parsing if necessary
            pass 
        
        reserve_datetime = datetime.fromisoformat(clean_time)
        now = datetime.now(reserve_datetime.tzinfo) # Use same timezone as input

        # Calculate the difference in minutes
        diff = now - reserve_datetime
        diff_minutes = diff.total_seconds() / 60

        logger.info(f"Reservation was made at {reserve_datetime}. Now is {now}. Delay: {diff_minutes:.2f} min")

        # Return 'cancelMinutes' back to Camunda
        return task.complete({"cancelMinutes": diff_minutes})

    except Exception as e:
        logger.error("Error calculating delay: %s", e)
        return task.failure("Calculation Error", str(e), 0, 0)

def handle_calculate_charge(task: ExternalTask) -> TaskResult:
    """Topic: calculate-charge"""
    logger.info("Calculating final amount to charge...")
    
    # In a real app, you'd calculate time difference here.
    base_cost = 15.00 # Simulated base cost for the ride
    
    return task.complete({"baseAmount": base_cost, "finalAmountToCharge": base_cost})

def handle_add_penalty(task: ExternalTask) -> TaskResult:
    """Topic: apply-penalty (add 10% penalty)"""
    logger.info("Applying 10% battery penalty")
    
    base_cost = task.get_variable("baseAmount") or 15.00
    penalty = base_cost * 0.10
    final_amount = base_cost + penalty
    
    return task.complete({"finalAmountToCharge": final_amount, "penaltyApplied": True})

def handle_rejection(task: ExternalTask) -> TaskResult:
    """Topic: notify-rejection (rental rejected)"""
    logger.warning("RENTAL REJECTED! Notifying systems...")
    return task.complete({})

