from logging import DEBUG, FileHandler, Formatter, getLogger

logger = getLogger("PythonTmx Logger")
logger.setLevel(DEBUG)
format_ = Formatter("%(asctime)s: %(levelname)s - %(funcName)s - \n%(message)s")
file_handler = FileHandler("logs.log", mode="w", encoding="utf-8")
file_handler.setFormatter(format_)
logger.addHandler(file_handler)
