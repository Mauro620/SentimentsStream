from enum import Enum


class SentimentLabel(str, Enum):
    POSITIVO = "positivo"
    NEGATIVO = "negativo"
    NEUTRAL = "neutral"

    @classmethod
    def from_string(cls, value: str) -> "SentimentLabel":
        for member in cls:
            if member.value == value.lower():
                return member
        raise ValueError(f"Unknown sentiment label: {value}")
