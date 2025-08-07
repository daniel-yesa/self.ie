import json
import os
from google.oauth2 import service_account

def get_credentials(env_var: str = "GOOGLE_APPLICATION_CREDENTIALS_JSON"):
    data = os.environ.get(env_var)
    if not data:
        raise RuntimeError(f"Missing environment variable: {env_var}")
    try:
        info = json.loads(data)
    except Exception as e:
        raise RuntimeError(f"Invalid JSON in {env_var}: {e}")
    return service_account.Credentials.from_service_account_info(info)
