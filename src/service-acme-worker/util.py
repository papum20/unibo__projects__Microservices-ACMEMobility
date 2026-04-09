from typing import Callable

from camunda.external_task.external_task import ExternalTask, TaskResult
import requests

from get_env import config



#
# REQUESTS
#

def func_success_status(
	status_var	: str
) -> Callable[[ExternalTask, requests.Response], TaskResult]:
	def _func_success(
		task		: ExternalTask,
		# pylint: disable=W0613
		response	: requests.Response,
	) -> TaskResult:
		return task.complete({status_var: True})
	return _func_success


def perform_request(
	task			: ExternalTask,
	func_request	: Callable,
	func_success	: Callable[[ExternalTask, requests.Response], TaskResult],
	action_name		: str,
	status_var		: str
) -> TaskResult:
	"""Helper to perform a fleet request with common error handling and logging."""
	config.logger.info("Starting %s", action_name)
	
	try:
		response = func_request()
		if response.status_code == 200:
			config.logger.info("%s completed successfully", action_name)
			return func_success(task, response)
		else:
			config.logger.error("Failed action %s: %s - %s", action_name, response.status_code, response.text)
			return task.complete({status_var: False})
	except requests.exceptions.Timeout:
		config.logger.error("%s timed out!", action_name)
		return task.failure(
			error_message	= f"{action_name} Timeout",
			error_details	= f"{action_name} took more than 10 seconds to respond.",
			max_retries		= REQUEST_MAX_RETRIES,
			retry_timeout	= REQUEST_RETRY_DELAY_MS
		)
	except Exception as e:
		config.logger.error("Connection Error: %s", e)
		return task.failure("Connection Error", str(e), 0, 0)



#
# SOAP
#

REQUEST_TIMEOUT_SECONDS = 10
REQUEST_MAX_RETRIES		= 3
REQUEST_RETRY_DELAY_MS	= 5000

SOAP_HEADERS = {'Content-Type': 'text/xml; charset=utf-8'}


def get_soap_body(body_content: str) -> str:
	return f"""<?xml version="1.0" encoding="UTF-8"?>
		<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
			<SOAP-ENV:Body>
				{body_content}
			</SOAP-ENV:Body>
		</SOAP-ENV:Envelope>"""

def soap_request(url: str, data: str) -> requests.Response:
	"""throws requests.exceptions.Timeout if the request takes too long"""
	return requests.post(url, data=data, headers=SOAP_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
