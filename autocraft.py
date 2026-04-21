import time
import random
from pynput.keyboard import Controller
from jsonHandler import getMacroSet
from exceptions import *
from models import MacroSet, AutomatedMacro
import threading

INTERACTION_KEY = 'h'
WAIT_TIME = 1
KEYBOARD = Controller()

pause_event: threading.Event = threading.Event()
resume_event: threading.Event = threading.Event()
stop_event: threading.Event = threading.Event()

progress: int = 0
crafting: bool = False

def getRandomTiming(originalTime: float) -> float:
    return originalTime + random.uniform(0,1)

def pressButton(button: str):
    KEYBOARD.press(button)
    time.sleep(getRandomTiming(0.3))
    KEYBOARD.release(button)

def startCraftingWindow():
    pressButton(INTERACTION_KEY)
    time.sleep(getRandomTiming(0.7))
    pressButton(INTERACTION_KEY)
    time.sleep(getRandomTiming(3))


def clearEvents():
    pause_event.clear()
    resume_event.clear()

def startCrafting(craftingDifficulty: str, iterations: int):
    global progress, crafting
    if(iterations == 0):
        return
    try:
        macroSet = getMacroSet(craftingDifficulty)
    except JsonHandlerException as e:
        print(str(e))
        return

    print(f"Waiting {WAIT_TIME} seconds before starting to craft")
    time.sleep(WAIT_TIME)

    progress = 0
    print("Crafting started")
    crafting = True
    while(progress < iterations):
        startCraftingWindow()
        print(f"Started new crafting: {progress}/{iterations}")
        counter = 0
        for macro in macroSet.macros:
            counter += 1
            pressButton(macro.keybind)
            time.sleep(getRandomTiming(macro.duration))
            if stop_event.is_set():
                crafting = False
                return
            print(f"Finished macro{counter}/{len(macroSet.macros)}")

        progress+=1
        
        if pause_event.is_set():
            crafting = False
            resume_event.wait()
            crafting = True
            if stop_event.is_set():
                crafting = False
                return
            clearEvents()
        else:
            time.sleep(getRandomTiming(4))

    print("FINISHED CRAFTING!")

