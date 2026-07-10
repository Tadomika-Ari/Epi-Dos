import os
import threading as Thread
import subprocess
import time
import stat
from src.core.voice_llm import llm
from src.core.llm_with_contexte import llm as llm_with_context
from src.core.waiting_message import waiting_message
import src.core.state as state


def minuteur():
    time_nb = 0
    while state.is_alive:
        if not state.time_statue:
            time_nb = 0
            state.time_statue = True
        time.sleep(1)
        time_nb = time_nb + 1    
        if time_nb > state.time_max:
            waiting_message()
            time_nb = 0

def open_kitty_shell():
    if os.path.exists(state.fifo_path):
        if not stat.S_ISFIFO(os.stat(state.fifo_path).st_mode):
            os.remove(state.fifo_path)
            os.mkfifo(state.fifo_path)
    else:
        os.mkfifo(state.fifo_path)
    subprocess.Popen(["kitty", "-e", "bash", "-c", f"tail -f {state.fifo_path} | bash"])

def send_command(cmd: str):
    with open(state.fifo_path, "w") as fifo:
        fifo.write(cmd + "\n")

def init_shell():
    open_kitty_shell()
    send_command("echo 'initialisation terminé.'")
    
def core():

    t_minuteur = Thread.Thread(target=minuteur, daemon=True)
    t_minuteur.start()

    t_talk = Thread.Thread(target=llm_with_context, daemon=True)
    t_talk.start()

    init_shell()
    while state.is_alive:
        if state.is_alive == 0:
            os.remove(state.fifo_path)
            break

            