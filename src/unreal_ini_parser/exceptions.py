class IniParserExceptionBase(Exception):
    pass


class SectionNotFoundException(IniParserExceptionBase):
    def __init__(self, section: str) -> None:
        super().__init__(f"Section {section} not found")


class KeyNotFoundException(IniParserExceptionBase):
    def __init__(self, key: str) -> None:
        super().__init__(f"Key {key} not found")


class KeyValueException(IniParserExceptionBase):
    def __init__(self, key, value, message) -> None:
        if value is None:
            super().__init__(f"\"{key}\": {message}")
        else:
            super().__init__(f"\"{key}={str(value)}\": {message}")
