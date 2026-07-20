import os
import sys
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_env_or_exit(key: str) -> str:
	val = os.environ.get(key)
	if val is None:
		logger.error("Missing required environment variable (make sure .env is configured in the parent directory): %s", key)
		sys.exit(2)
	return val
