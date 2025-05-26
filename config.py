import os
from dotenv import load_dotenv
import json 

load_dotenv(override=True)

PHLEBOTOMISTS = json.loads(os.getenv("PHLEBOTOMISTS", [1, 2, 3, 4, 5, 6, 7]))
INTERVAL = 120
DURATION = 60 * int(os.getenv("DURATION", 60)) # 60 minutes
API_URL = "https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test/clinicianstatus"
LOW_LEVEL = 0.5
MID_LEVEL = 1.0
SENDER = os.getenv('SENDER')
PASSWORD = os.getenv("PASSWORD")
RECEPIENT = os.getenv("RECEPIENT")
REDIS_USED = os.getenv("REDIS_BOOL", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ALERTS_USED = os.getenv("ALERT_USED", "false").lower() == "true"
