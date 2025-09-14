import os
from dotenv import load_dotenv

load_dotenv()

TOKEN_TELEGRAM = os.getenv('TOKEN_TELEGRAM')
DSN = os.getenv('DSN')