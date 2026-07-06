import requests
from src.ctOS.music.get_token_tmp import get_token

def resume():
    access_token = get_token()
    url = "https://api.spotify.com/v1/me/player/play"
    header = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
    data = {}
    result = requests.put(url, headers=header, json=data)
    try:
        body = result.json()
    except Exception:
        body = result.text
    print(body)
    print(result.status_code)