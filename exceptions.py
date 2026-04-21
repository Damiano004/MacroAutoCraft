class JsonHandlerException(Exception):
    def __init__(self, message):
        super().__init__(message)
    
class MacroExtractorException(Exception):
    def __init__(self, message):
        super().__init__(message)