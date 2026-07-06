import os
import sys
from src.ctOS.light.toggle_light import toggle_light

def light_command():
    nb  = len(sys.argv)

    if nb <= 2:
        print("no argument give. Please give word")
        return
    if sys.argv[2] == "toggle":
        toggle_light()
        return
    else:
        print("no argument give. Please give word")