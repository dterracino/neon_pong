"""
Interpolator — generic linear interpolation across numeric types, tuples, and lists.
"""
from __future__ import annotations

from numbers import Real
from typing import Any, cast


class Interpolator:
    @staticmethod
    def lerp(start: Any, end: Any, t: float) -> Any:
        if isinstance(start, Real) and isinstance(end, Real):
            return cast(float, start) + (cast(float, end) - cast(float, start)) * t

        if isinstance(start, tuple) and isinstance(end, tuple):
            if len(start) != len(end):
                raise ValueError("Tuple interpolation requires equal lengths.")
            return tuple(
                Interpolator.lerp(s, e, t)
                for s, e in zip(start, end, strict=True)
            )

        if isinstance(start, list) and isinstance(end, list):
            if len(start) != len(end):
                raise ValueError("List interpolation requires equal lengths.")
            return [
                Interpolator.lerp(s, e, t)
                for s, e in zip(start, end, strict=True)
            ]

        lerp_method = getattr(start, "lerp", None)
        if callable(lerp_method):
            return lerp_method(end, t)

        raise TypeError(
            f"Unsupported interpolation types: {type(start).__name__} -> {type(end).__name__}"
        )
