'''
Configure logger
'''
import logging
from pathlib import Path
Path("/app").mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename="/app/asscan.log",
    level=logging.DEBUG,
    format="[%(asctime)s] [%(filename)s:%(lineno)s - %(funcName)5s() - %(processName)s] %(levelname)s - %(message)s"
)