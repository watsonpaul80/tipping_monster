from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Tip:
    """Typed representation of a single betting tip."""

    race: str = ""
    name: str = ""
    confidence: float = 0.0
    bf_sp: Optional[float] = None
    odds: Optional[float] = None
    realistic_odds: Optional[float] = None
    stake: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    commentary: Optional[str] = None
    monster_mode: bool = False
    explanation: Optional[str] = None
    stable_form: Optional[float] = None
    extras: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.tags, str):
            self.tags = [self.tags]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dataclass_fields__:  # type: ignore[attr-defined]
            return getattr(self, key)
        return self.extras.get(key)

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.__dataclass_fields__:  # type: ignore[attr-defined]
            return getattr(self, key, default)
        return self.extras.get(key, default)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self.__dataclass_fields__:  # type: ignore[attr-defined]
            setattr(self, key, value)
        else:
            self.extras[key] = value

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tip":
        fields = cls.__dataclass_fields__.keys()  # type: ignore[attr-defined]
        known = {k: data[k] for k in data.keys() if k in fields}
        extras = {k: v for k, v in data.items() if k not in fields}
        tip = cls(**known)
        tip.extras.update(extras)
        return tip

    def to_dict(self) -> Dict[str, Any]:
        base = {
            k: getattr(self, k)
            for k in self.__dataclass_fields__  # type: ignore[attr-defined]
            if k != "extras"
        }
        base.update(self.extras)
        return base
