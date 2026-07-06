#!/usr/bin/env python3
import requests
import time
import random
from collections import deque
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.panel import Panel

console = Console()
GREEN = "bold spring_green2"
DIM_GREEN = "spring_green4"

BOOT_LINES = [
    "[INIT] Loading all module...",
    "[NET ] Establishing uplink to backbone...",
    "[OK  ] All systems are onlines.",
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

def make_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="main", ratio=2),
    )
    return layout

def render_status(history: deque) -> Panel:
    body = Text("\n".join(history), style=DIM_GREEN)
    return Panel(body, border_style=DIM_GREEN)

def start():
    layout = make_layout()
    history = deque(maxlen=6)
    messages = BOOT_LINES
    start = START_LINE
    wait = WAITING_LINE
    is_finish = False

    with Live(layout, console=console, refresh_per_second=20, screen=True):
        while is_finish is False:
            history = None
            history = deque(maxlen=6)
            history.append(start[0])
            layout["main"].update(render_status(history))