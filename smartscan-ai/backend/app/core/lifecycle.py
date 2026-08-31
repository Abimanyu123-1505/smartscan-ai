from .logging import logger

async def startup_handler():
    logger.info("Application starting up...")

async def shutdown_handler():
    logger.info("Application shutting down...")
