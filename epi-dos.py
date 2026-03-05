#!/usr/bin/env python3

from hand_detection import main
from object_detection import object
from voice_llm import llm


def init():
    print("\n")
    print("Bonjour utilisateur\n")
    print("Que voulez vous faire ?\n")
    print("0 : hand detection.\n")
    print("1 : object detection\n")
    print("2 : llm with voice Glados\n")
    print("3 : voice to voice with GlaDOS\n")
    choice = input("donne ton choix : ")

    if (int(choice) == 0):
        main()
    if (int(choice) == 1):
        object()
    if (int(choice) == 2):
        llm()
    if (int(choice) != 0):
        return

if __name__ == "__main__":
    init()
