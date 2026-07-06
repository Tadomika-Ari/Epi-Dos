import requests
from src.ctOS.music.get_token_tmp import get_token

def pause():
    access_token = get_token()
    url = "https://api.spotify.com/v1/me/player/pause"
    header = {"Authorization": "Bearer " + access_token}

    result = requests.put(url, headers=header)
    try:
        body = result.json()
    except Exception:
        body = result.text
    print(body)
    print(result.status_code)