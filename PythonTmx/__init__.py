from logging import DEBUG, FileHandler, Formatter, getLogger

logger = getLogger(__name__)
logger.setLevel(DEBUG)
loggerFileHandler = FileHandler("logs.log")
loggerFileHandler.setFormatter(
    Formatter("%(asctime)s - %(levelname)s - %(module)s:\n%(message)s")
)
logger.addHandler(loggerFileHandler)
