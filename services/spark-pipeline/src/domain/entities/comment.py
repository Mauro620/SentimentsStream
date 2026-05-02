from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Comment:
    id: int
    texto: str
    sentimiento: str
    fecha: str
    text_clean: Optional[str] = None
