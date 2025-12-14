from dataclasses import dataclass


@dataclass
class Codepoint:
    value: int

    def __repr__(self) -> str:
        return f"U+{self.value:04X}"

    @staticmethod
    def from_string(s: str) -> "Codepoint":
        if not s.startswith("U+"):
            raise ValueError(f"Invalid codepoint string: {s}")
        value = int(s[2:], 16)
        return Codepoint(value)
