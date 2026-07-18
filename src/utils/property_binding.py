"""
PropertyBinding — a getter/setter pair that attaches a Tween to a live property.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(slots=True)
class PropertyBinding:
    getter: Callable[[], Any]
    setter: Callable[[Any], None]
    target: Any | None = None
    property_name: str | None = None

    def get(self) -> Any:
        return self.getter()

    def set(self, value: Any) -> None:
        self.setter(value)

    @staticmethod
    def for_attribute(target: Any, attr_name: str) -> PropertyBinding:
        return PropertyBinding(
            getter=lambda: getattr(target, attr_name),
            setter=lambda value: setattr(target, attr_name, value),
            target=target,
            property_name=attr_name,
        )

    @staticmethod
    def for_dict_key(target: dict[str, Any], key: str) -> PropertyBinding:
        return PropertyBinding(
            getter=lambda: target[key],
            setter=lambda value: target.__setitem__(key, value),
            target=target,
            property_name=key,
        )

    @staticmethod
    def for_list_index(target: list[Any], index: int) -> PropertyBinding:
        return PropertyBinding(
            getter=lambda: target[index],
            setter=lambda value: target.__setitem__(index, value),
            target=target,
            property_name=str(index),
        )
