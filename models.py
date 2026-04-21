from pydantic import BaseModel

class AutomatedMacro(BaseModel):
    keybind: str
    duration: int

class MacroSet(BaseModel):
    difficulty: str
    macros: list[AutomatedMacro]

class MacroDictionary(BaseModel):
    macroDictionary: list[MacroSet]

class UserMacro():
    keybind: str
    content: str