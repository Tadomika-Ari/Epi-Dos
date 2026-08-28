import os
from pathlib import Path
from src.ctOS.music.get_token_tmp import get_token
import time

PATH_TOKEN = "src/music/.spotify_token.json"

def init():
    p = Path(".env")
    if not p.exists():
        print("Pas de .env detecter. Veuillez en créer un")
        return 84
    
    token_public = os.getenv("TOKEN_PUBLIC")
    token_private = os.getenv("TOKEN_PRIVATE")
    if not token_public or not token_private:
        print("Pas de token detecter. Veuillez vous referer a la doc pour pouvoir en obtenir")
        time.sleep(2)
        return 84

    p = Path(PATH_TOKEN)
    if not p.exists():
        print("Premier utilisation detecter. Redirection vers la connection spotify")
        time.sleep(2)
        get_token()

    token_discord = os.getenv("API_KEY")
    if not token_discord:
        print("Pas de Clef API pour connecter Tranquility au bot discord. Si vous souhaitez l'utiliser inscrivez vous au bot discord et mettez la clef api dans le .env")
    else:
        print("Clef API est détécter. L'integration discord est donc disponible.")
        time.sleep(2)
    print("Tous est désormais initialisé. Veuillez faire ctOS --start")
    time.sleep(2)