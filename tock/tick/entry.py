from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Dict


@dataclass
class TickEntry(object):
    
    __slots__ = ["date", "hours", "notes", "task_id", "user_id"]
    
    date: date
    hours: float
    notes: str
    task_id: int

    def serialize(self) -> Dict[Any, Any]:
        serialized_data = {}
        for k, v in asdict(self).items():
            if v:
                if isinstance(v, date):
                    v = v.strftime("%Y-%m-%d")
                serialized_data.update({k: v})
        return serialized_data
