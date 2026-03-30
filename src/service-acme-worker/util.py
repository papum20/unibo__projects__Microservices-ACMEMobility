
import os
import sys

import requests



def get_env_or_exit(key: str) -> str:
	val = os.environ.get(key)
	if val is None:
		print(f"Missing required environment variable (make sure .env is configured in the parent directory): {key}", file=sys.stderr)
		sys.exit(2)
	return val


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
