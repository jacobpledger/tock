from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Dict


@dataclass
class Serializable:
    """
    NOTE: Subclasses of Serializable must also be dataclasses.
    """

    def serialize(self) -> Dict[Any, Any]:
        serialized_data = {}
        for k, v in asdict(self).items():
            if v:
                if isinstance(v, date):
                    v = v.strftime("%Y-%m-%d")
                if isinstance(v, datetime):
                    v = v.strftime("%Y-%m-%dT%H:%M:%S")
                serialized_data.update({k: v})
        return serialized_data
