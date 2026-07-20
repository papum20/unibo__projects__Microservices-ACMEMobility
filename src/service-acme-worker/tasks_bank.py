import requests
import xml.etree.ElementTree as ET
from camunda.external_task.external_task import ExternalTask, TaskResult

from db import DATABASE, Vehicle
from get_env import config
from util import (
	get_soap_body,
	perform_request,
	soap_request,
)



# =====================================================================
# BANK SERVICES (SOAP)
# =====================================================================

def handle_bank_preauth(task: ExternalTask) -> TaskResult:
	"""Topic: bank-preauth (block 10€ caution money)"""
	
	user	= DATABASE.get_user(task.get_variable(config.CAMUNDA_USER_ID))
	if user is None:
		config.logger.error("User %s not found or has no saved card!", task.get_variable(config.CAMUNDA_USER_ID))
		return task.failure("User Not Found or No Saved Card", f"User {task.get_variable(config.CAMUNDA_USER_ID)} not found or has no saved card.", 0, 0)

	card_id		= user.saved_card
	if card_id is None:
		config.logger.error("User %s has no saved card!", task.get_variable(config.CAMUNDA_USER_ID))
		return task.failure("User Not Found or No Saved Card", f"User {task.get_variable(config.CAMUNDA_USER_ID)} not found or has no saved card.", 0, 0)

	soap_body	= get_soap_body(
		f"""<{config.EP_BANK_PREAUTH}>
			<cardId>{card_id}</cardId>
			<amount>{config.BANK_CAUTION}</amount>
		</{config.EP_BANK_PREAUTH}>""")

	def func_success(
		task		: ExternalTask,
		# pylint: disable=W0613
		response	: requests.Response
	) -> TaskResult:
		root = ET.fromstring(response.content)
			
		# search for the tags, ignoring namespaces, using ".//"
		token_element   = root.find(".//token")
		success_element = root.find(".//success")
		
		if token_element is not None:
			token   = token_element.text
			success = (success_element.text == 'true')  # type: ignore
			
			config.logger.info("Bank PreAuth Success! Token: %s", token)
			
			# Save the token to Camunda variables
			return task.complete({
				config.CAMUNDA_BANK_TOKEN				: token,
				config.CAMUNDA_STATUS_CAUTION_BLOCKED	: success
			})
		else:
			config.logger.error("Bank PreAuth failed! Could not find <token> in SOAP response.")
			return task.bpmn_error(
				error_code		= "Parse Error",
				error_message	= "Could not find <token> in SOAP response",
				variables		= {config.CAMUNDA_STATUS_CAUTION_BLOCKED: False}
			)


	return perform_request(
		task,
		func_request	= lambda: soap_request(config.URL_BANK_WSDL, soap_body),
		action_name		= "Bank PreAuth",
		status_var		= config.CAMUNDA_STATUS_CAUTION_BLOCKED,
		func_success	= func_success
	)


def handle_bank_charge(task: ExternalTask) -> TaskResult:
	"""Topic: bank-charge (charge user)"""
	
	# Get variables from Camunda context
	token		= task.get_variable(config.CAMUNDA_BANK_TOKEN)
	amount		= task.get_variable(config.CAMUNDA_AMOUNT_TO_CHARGE)
	soap_body	= get_soap_body(
		f"""<{config.EP_BANK_CHARGE}>
			<token>{token}</token>
			<amount>{amount}</amount>
		</{config.EP_BANK_CHARGE}>""")

	def func_success(
		task		: ExternalTask,
		# pylint: disable=W0613
		response	: requests.Response
	) -> TaskResult:
		root = ET.fromstring(response.content)
		status_element = root.find(".//status")
		
		if status_element is not None:
			status = status_element.text
			config.logger.info("Bank Charge Status: %s", status)
			
			return task.complete({config.CAMUNDA_STATUS_PAYMENT: status})
		else:
			config.logger.error("Bank Charge failed! Could not find <status> in SOAP response.")
			return task.bpmn_error(
				error_code		= "Parse Error",
				error_message	= "Could not find <status> in SOAP response",
				variables		= {config.CAMUNDA_STATUS_PAYMENT: "Error"}
			)

	return perform_request(
		task,
		func_request	= lambda: soap_request(config.URL_BANK_WSDL, soap_body),
		action_name		= "Bank Charge",
		status_var		= config.CAMUNDA_STATUS_PAYMENT,
		func_success	= func_success
	)
	

def handle_bank_unlock_caution(task: ExternalTask) -> TaskResult:
	"""Topic: bank-unlock-caution"""

	token		= task.get_variable(config.CAMUNDA_BANK_TOKEN)
	soap_body	= get_soap_body(
		f"""<{config.EP_BANK_UNLOCK_CAUTION}>
			<token>{token}</token>
		</{config.EP_BANK_UNLOCK_CAUTION}>""")

	def func_success(
		task		: ExternalTask,
		# pylint: disable=W0613
		response	: requests.Response
	) -> TaskResult:
		root = ET.fromstring(response.content)
		success_element = root.find(".//success")
		
		if success_element is not None:
			success = (success_element.text == 'true')  # type: ignore
			config.logger.info("Bank Unlock Caution Success: %s", success)
			return task.complete({config.CAMUNDA_STATUS_CAUTION_UNLOCKED: success})
		else:
			config.logger.error("Bank Unlock Caution failed! Could not find <success> in SOAP response.")
			return task.bpmn_error(
				error_code		= "Parse Error",
				error_message	= "Could not find <success> in SOAP response",
				variables		= {config.CAMUNDA_STATUS_CAUTION_UNLOCKED: False}
			)

	return perform_request(
		task,
		func_request	= lambda: soap_request(config.URL_BANK_WSDL, soap_body),
		action_name		= "Bank Unlock Caution",
		status_var		= config.CAMUNDA_STATUS_CAUTION_UNLOCKED,
		func_success	= func_success
	)


def handle_bank_convert_caution(task: ExternalTask) -> TaskResult:
	"""Topic: bank-convert-caution (convert blocked caution into actual charge)"""

	# first set the vehicle to available again
	vehicle_id	= task.get_variable(config.CAMUNDA_VEHICLE_ID)
	vehicle		= DATABASE.get_vehicle(vehicle_id)

	if vehicle is None:
		config.logger.error("Vehicle %s not found!", vehicle_id)
		return task.failure("Vehicle Not Found", f"Vehicle {vehicle_id} not found.", 0, 0)

	DATABASE.update_vehicle( Vehicle(
		vehicle_id		= vehicle_id,
		status			= Vehicle.Status.AVAILABLE,
		reserved_by		= None,
		rented_by		= None,
		current_station	= vehicle.current_station,
		battery_perc	= vehicle.battery_perc
	))


	token		= task.get_variable(config.CAMUNDA_BANK_TOKEN)
	soap_body	= get_soap_body(
		f"""<{config.EP_BANK_CONVERT_CAUTION}>
			<token>{token}</token>
		</{config.EP_BANK_CONVERT_CAUTION}>""")

	def func_success(
		task		: ExternalTask,
		# pylint: disable=W0613
		response	: requests.Response
	) -> TaskResult:
		root = ET.fromstring(response.content)
		status_element = root.find(".//status")
		
		if status_element is not None:
			status = status_element.text
			config.logger.info("Bank Convert Caution Status: %s", status)
			
			return task.complete({config.CAMUNDA_STATUS_CONVERT_CAUTION: status})
		else:
			config.logger.error("Bank Convert Caution failed! Could not find <status> in SOAP response.")
			return task.bpmn_error(
				error_code		= "Parse Error",
				error_message	= "Could not find <status> in SOAP response",
				variables		= {config.CAMUNDA_STATUS_CONVERT_CAUTION: "Error"}
			)

	return perform_request(
		task,
		func_request	= lambda: soap_request(config.URL_BANK_WSDL, soap_body),
		action_name		= "Bank Convert Caution",
		status_var		= config.CAMUNDA_STATUS_CONVERT_CAUTION,
		func_success	= func_success
	)
	
