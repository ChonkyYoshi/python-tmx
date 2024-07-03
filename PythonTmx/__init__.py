from logging import DEBUG, FileHandler, Formatter, basicConfig, getLogger

logger = getLogger()
basicConfig(level=DEBUG, filename="logs.log", filemode="w")
