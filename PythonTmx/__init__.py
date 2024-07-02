from logging import DEBUG, FileHandler, Formatter, LoggerAdapter, getLogger

_logger = getLogger("PythonTmx")
_logger.setLevel(DEBUG)
loggerFileHandler = FileHandler("logs.log")
loggerFileHandler.setFormatter(
    Formatter(
        "%(asctime)s - %(levelname)s - %(module)s - %(ClassName)s - %(funcName)s\n%(message)s"
    )
)
_logger.addHandler(loggerFileHandler)
