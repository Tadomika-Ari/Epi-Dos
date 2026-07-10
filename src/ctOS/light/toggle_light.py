import os
import subprocess

FIFO_PATH = "/tmp/kitty_shell_input"
CMD_LIGHT = "./ecc-api --toggle"

def toggle_light():
    if not os.path.exists(FIFO_PATH):
        print(f"Sub-Agent: FIFO introuvable: {FIFO_PATH}")
        return
    with open(FIFO_PATH, "w") as fifo:
        fifo.write(CMD_LIGHT + "\n")
    subprocess.run(CMD_LIGHT)
    return

def toggle_light():
    subprocess.run(CMD_LIGHT)
    return