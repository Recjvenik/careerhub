import urllib.request
import json
from django.conf import settings

def fetch_phone_email_data(user_json_url):
    """
    Fetches user data from Phone Email JSON URL.
    Returns a dictionary with user info or None if failed.
    """
    try:
        with urllib.request.urlopen(user_json_url) as url:
            data = json.loads(url.read().decode())
            return data
    except Exception as e:
        print(f"Error fetching Phone Email data: {e}")
        return None
