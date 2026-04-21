import json
from exceptions import *
from models import MacroDictionary, MacroSet, UserMacro
from macroExctractor import extractMacro
from pathlib import Path

JSON_FILE_PATH: Path = Path("data/macros.json")
MACRO_DICT: MacroDictionary

def importData():
    JSON_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if not JSON_FILE_PATH.exists():
        with open(JSON_FILE_PATH, "w") as f:
            json.dump({"macroDictionary": []}, f, indent=4)

    with open(JSON_FILE_PATH, "r") as file:
        json_data = json.load(file)
    
    global MACRO_DICT
    MACRO_DICT = MacroDictionary(**json_data)

def addNewMacro(difficulty: str, userMacroList: list[UserMacro]):
    macros = [extractMacro(userMacro) for userMacro in userMacroList]
    macroSet = MacroSet(difficulty=difficulty, macros=macros)
    MACRO_DICT.macroDictionary.append(macroSet)
    saveCurrentList()

def removeMacro(difficulty: str):
    try:
        macroSet = getMacroSet(difficulty)
    except JsonHandlerException as e:
        print(e)
        return

    MACRO_DICT.macroDictionary.remove(macroSet)
    saveCurrentList()

def saveCurrentList():
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(MACRO_DICT.model_dump(), f, ensure_ascii=False, indent=4)


def getMacroSet(difficulty: str) -> MacroSet:
    try:
        return next(macro for macro in MACRO_DICT.macroDictionary if macro.difficulty == difficulty)
    except(StopIteration):
        raise JsonHandlerException("No macro set found with difficulty "+difficulty)