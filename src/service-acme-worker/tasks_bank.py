import requests
import xml.etree.ElementTree as ET
from camunda.external_task.external_task import ExternalTask, TaskResult

from db import DATABASE
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
			return task.failure("Parse Error", "Could not find <token> in SOAP response", 0, 0)


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
			return task.failure("Parse Error", "Could not find <status> in SOAP response", 0, 0)

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
			return task.complete({"cautionUnlocked": success})
		else:
			return task.failure("Parse Error", "Could not find <success> in SOAP response", 0, 0)

	return perform_request(
		task,
		func_request	= lambda: soap_request(config.URL_BANK_WSDL, soap_body),
		action_name		= "Bank Unlock Caution",
		status_var		= config.CAMUNDA_STATUS_CAUTION_UNLOCKED,
		func_success	= func_success
	)


def handle_bank_convert_caution(task: ExternalTask) -> TaskResult:
	"""Topic: bank-convert-caution (convert blocked caution into actual charge)"""

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
			return task.failure("Parse Error", "Could not find <status> in SOAP response", 0, 0)

	return perform_request(
		task,
		func_request	= lambda: soap_request(config.URL_BANK_WSDL, soap_body),
		action_name		= "Bank Convert Caution",
		status_var		= config.CAMUNDA_STATUS_CONVERT_CAUTION,
		func_success	= func_success
	)
	
