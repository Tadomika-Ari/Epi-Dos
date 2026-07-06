#!/usr/bin/env python3
import time
import random
from collections import deque
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

console = Console()
GREEN = "bold spring_green2"
DIM_GREEN = "spring_green4"

BOOT_LINES = [
    "[INIT] Check env is created",
    "[OK  ] Env check",
    "[INIT] Check env variable",
    "[OK  ] Variable good",
    "[INIT] Check spotify section",
    "[OK  ] Token is good",
    "[INIT] Check other command",
    "[OK  ] Other command good",
    "[INIT] Start cli...",
]

SPACE_LINE = [
    " "
]

WAITING_LINE = [
    "."
    ".."
    "..."
]

START_LINE = [
    "Hello from ctOS"
]

ERROR_LINE = "Error detected. First time to use ? Use ctOS --init"

def make_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="main", ratio=2),
        Layout(name="bottom", size=9),
    )
    layout["bottom"].split_row(
        Layout(name="bottom_left"),
    )
    return layout

def render_center(percent: int, width: int = 40) -> Align:
    filled = int(width * percent / 100)
    empty = width - filled
    bar_str = "█" * filled + "░" * empty
    text = Text(f"{bar_str} {percent:3d}%", style=GREEN, justify="center")
    return Align.center(text, vertical="middle")

def render_status(history: deque) -> Panel:
    body = Text("\n".join(history), style=DIM_GREEN)
    return Panel(body, border_style=DIM_GREEN)

def check_file_env():
    p = Path(".env")
    if p.exists():
        return 0
    else:
        return 84

def check_token():
    p = Path("src/music/.spotify_token.json")
    if p.exists():
        return 0
    else:
        return 84

def check_variable():
    token_public = os.getenv("TOKEN_PUBLIC")
    token_private = os.getenv("TOKEN_PRIVATE")
    if not token_public or not token_private:
        return 84
    else:
        return 0

STEPS = [
    ("[INIT] Check env is created",     None),
    ("[OK  ] Env check",                check_file_env),
    ("[INIT] Check env variable",       None),
    ("[OK  ] Variable good",            check_variable),
    ("[INIT] Check spotify section",    None),
    ("[OK  ] Token is good",            check_token),
    ("[INIT] Check other command",      None),
    ("[OK  ] Other command good",       None),
    ("[INIT] Start cli...",             None),
]

def demo():
    layout = make_layout()
    history = deque(maxlen=6)

    with Live(layout, console=console, refresh_per_second=20, screen=True):
        for i, (label, check) in enumerate(STEPS):
            history.append(label)

            if check is not None:
                r = check()
                if r == 84:
                    history.append(ERROR_LINE)
                    time.sleep(2)
                    return 84

            percent = ((i + 1) * 100) // len(STEPS)
            layout["main"].update(render_center(percent))
            layout["bottom_left"].update(render_status(history))
            time.sleep(1)

if __name__ == "__main__":
    demo()