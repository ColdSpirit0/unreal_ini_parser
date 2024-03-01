class IniParserExceptionBase(Exception):
    pass


class SectionNotFoundException(IniParserExceptionBase):
    def __init__(self, section: str, message: str = "Section %s not found") -> None:
        super().__init__(message.format(section))


class KeyNotFoundException(IniParserExceptionBase):
    def __init__(self, key: str) -> None:
        super().__init__(f"Key {key} not found")


class KeyValueException(IniParserExceptionBase):
    def __init__(self, key, value, message) -> None:
        if value is None:
            super().__init__(f"\"{key}\": {message}")
        else:
            super().__init__(f"\"{key}={str(value)}\": {message}")
