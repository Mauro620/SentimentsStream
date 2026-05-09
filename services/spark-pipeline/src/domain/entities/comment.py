from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Comment:
    id: int
    texto: str
    sentimiento: str
    ingested_at: datetime
    text_clean: Optional[str] = None

    @property
    def fecha(self) -> str:
        return self.ingested_at.strftime("%Y-%m-%d")
