import logging
import os
from datetime import datetime

from prime_league_bot.settings import LOGGING_DIR

logging.basicConfig(
    filename=os.path.join(LOGGING_DIR, f"notifications_{datetime.now().strftime('%Y-%m-%d')}.log"),
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)

logger = logging.getLogger()
