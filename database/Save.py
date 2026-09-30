import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Save:
    id: int
    user_id: int
    name: str = "Default Save"
    count: int = 0
    creation_date: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Save":
        raw_date = row["creationDate"]

        return cls(
            id=row["id"],
            user_id=row["userId"],
            name=row["name"],
            count=row["count"],
            creation_date=row["creationDate"]
        )