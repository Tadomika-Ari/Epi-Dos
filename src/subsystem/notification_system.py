import json
import os
import requests
import secrets
from pathlib import Path
import asyncio
import httpx

async def send_discord_message(text: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://gla-dos-prod.up.railway.app/discord/say",
            json={"text": text},
            headers={"X-Glados-Key": os.getenv("API_KEY")},
        )
        r.raise_for_status()
        return r.json()


def sendMessage(message):
    p = Path(".env")
    if not p.exists():
        print("Pas de .env detecter. Veuillez en créer un")
        return 84
        
    my_key = os.getenv("API_KEY")
    return 0

