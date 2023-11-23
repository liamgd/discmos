from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class Emoji:
    id: int
    name: str
    server: str


@dataclass(frozen=True)
class EmojiData:
    servers: Set[str]
    emojis: Set[Emoji]
