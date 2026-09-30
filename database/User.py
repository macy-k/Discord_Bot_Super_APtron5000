import sqlite3
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    active_save: Optional[int] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "User":
        return cls(id=row["id"],
                   active_save=row["activeSave"])