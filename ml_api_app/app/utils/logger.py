import logging

# Configure logging
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

# Add handlers to the loggers
api_logger.addHandler(api_handler)
ai_logger.addHandler(ai_handler)
