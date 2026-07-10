import requests
import json
import sys
from src.ctOS.music.get_token_tmp import get_token
import requests

def get_id_device():
    access_token = get_token()
    url = "https://api.spotify.com/v1/me/player/devices"
    header = {"Authorization": "Bearer " + access_token}

    result = requests.get(url, headers=header)
    try:
        body = result.json()
    except Exception:
        body = result.text
    print(body)
