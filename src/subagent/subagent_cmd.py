import os
import re
import src.core.state as state

def send_command(cmd: str):
    if not os.path.exists(state.fifo_path):
        print(f"Sub-Agent: FIFO introuvable: {state.fifo_path}")
        return
    with open(state.fifo_path, "w") as fifo:
        fifo.write(cmd + "\n")

def subagent_cmd(cmd: str):
    cmd_s = re.search(r"<cmd>(.*?)</cmd>", cmd)
    if cmd_s:
        send_command(cmd_s.group(1))
    else:
        return 