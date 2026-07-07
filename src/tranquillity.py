import sys
from pathlib import Path
from src.core.voice_llm import llm
from src.core.llm_with_contexte import llm as llm_with_contexte
from src.core.core import core
from src.core.waiting_message import waiting_message
from src.core.fast import main as llm_fast

def init():
    print("\n")
    print("Bonjour utilisateur\n")
    print("Que voulez vous faire ?\n")
    print("1 : llm with voice.\n")
    print("2 : llm with context and voice.\n")
    print("3 : with threading\n")
    print("4 : waiting message\n")
    print("5 : fast message")
    choice = input("donne ton choix : ")

    if (int(choice) == 1):
        llm()
    if (int(choice) == 2):
        llm_with_contexte()
    if (int(choice) == 3):
        core()
    if (int(choice) == 4):
        waiting_message()
    if (int(choice) == 5):
        llm_fast()
    if (int(choice) != 0):
        return

if __name__ == "__main__":
    init()
