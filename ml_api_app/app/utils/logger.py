import logging

import sys

# Configure logging to also print to stdout
logging.basicConfig(level=logging.INFO)
api_logger = logging.getLogger('api_logger')
ai_logger = logging.getLogger('ai_logger')

# Create handlers
api_handler = logging.FileHandler('api_log.log')
ai_handler = logging.FileHandler('ai_log.log')

# Set level for handlers
api_handler.setLevel(logging.INFO)
ai_handler.setLevel(logging.INFO)

# Create formatters and add them to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
api_handler.setFormatter(formatter)
ai_handler.setFormatter(formatter)

# Add stream handler to print to stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

# Add handlers to the loggers
api_logger.addHandler(stream_handler)
ai_logger.addHandler(stream_handler)
api_logger.addHandler(api_handler)
ai_logger.addHandler(ai_handler)
