class CleanedText:
    def __init__(self, value: str) -> None:
        if not value:
            raise ValueError("CleanedText cannot be empty")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CleanedText):
            return False
        return self._value == other._value

    def __repr__(self) -> str:
        return f"CleanedText({self._value!r})"
