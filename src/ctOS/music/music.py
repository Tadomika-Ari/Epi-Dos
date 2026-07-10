import requests
import json
import sys
from src.ctOS.music.get_token_tmp import get_token
import requests
from src.ctOS.music.get_id_device import get_id_device
from src.ctOS.music.pause import pause
from src.ctOS.music.resume import resume

def music_command():
    nb  = len(sys.argv)

    if nb <= 2:
        print("no argument give. Please give word")
        return
    if sys.argv[2] == "device":
        get_id_device()
        return
    if sys.argv[2] == "pause":
        pause()
        return
    if sys.argv[2] == "resume":
        resume()
        return
    else:
        print("no argument give. Please give word")
