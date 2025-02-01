import os
from json import loads
from typing import Final, List

from dotenv import load_dotenv

load_dotenv()

TOKEN: Final[str] = os.getenv('TELEGRAM')
OPENAPI: Final[str] = os.getenv('OPENAPI')
LLM_PATH: Final[str] = os.getenv('LLM_PATH')
PORT: Final[int] = int(os.getenv("PORT", 8080))
ADMINS: Final[List[int]] = loads(os.getenv('ADMINS'))

TELEGRAM_EDIT_DELAY = 8



