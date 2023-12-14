from requests import get
from constants import GOOGLE_DISCOVERY_URL

def get_google_provider_cfg():
    return get(GOOGLE_DISCOVERY_URL).json()
