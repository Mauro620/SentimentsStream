from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.comment import Comment


class CommentSource(ABC):
    @abstractmethod
    def get_all(self) -> List[Comment]:
        pass

    @abstractmethod
    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        pass


class BatchCommentSource(CommentSource):
    """Read comments from a batch source (e.g., parquet file)."""

    @abstractmethod
    def get_batch(self, limit: Optional[int] = None) -> List[Comment]:
        pass
