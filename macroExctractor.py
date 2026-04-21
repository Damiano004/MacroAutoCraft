import re
from exceptions import *
from models import UserMacro, AutomatedMacro

def extractDuration(macroRows: list[str]) -> int:
    macroDuration = 0
    for row in macroRows:
        if "/ac" not in row:
            continue
        match = re.search(r'<wait\.(\d)>', row)
        if match:
            macroDuration += int(match.group(1))
    return macroDuration

def extractMacro(macro: UserMacro) -> AutomatedMacro:
    if not macro:
        raise MacroExtractorException("Can't extract macro, given macro was null")
    
    macroRows = macro.content.split("\n")
    print(f'macro rows: {len(macroRows)}')
    macroDuration = extractDuration(macroRows)
    
    print(f"Macro extraction resulted with a macro with duration {macroDuration}")
    if macroDuration == 0:
        raise MacroExtractorException("Macro can't have duration = 0")
    
    return AutomatedMacro(keybind=macro.keybind, duration=macroDuration + 2)