import os
from json import loads
from typing import Final, List

from dotenv import load_dotenv

load_dotenv()

TOKEN: Final[str] = os.getenv('TELEGRAM')
PORT: Final[int] = int(os.getenv("PORT", 8080))
ADMINS: Final[List[int]] = loads(os.getenv('ADMINS'))
OPENROUTER_API_KEY: Final[str] = os.getenv('OPENROUTER_API_KEY')

TELEGRAM_EDIT_DELAY = 7



