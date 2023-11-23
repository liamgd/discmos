import re
from typing import List, Set

from .classes import Emoji, EmojiData
from .constants import (
    ALL_SEARCH,
    PREFIXES,
    REGEX_SEARCH,
    SPECIFIC_SEARCH,
    Mode,
)


def filter_emojis(emoji_data: EmojiData, include: str) -> List[Emoji]:
    emojis: Set[Emoji] = set()
    current_servers = []
    lines = include.split('\n')

    for line in lines:
        if line == '' or line.startswith('// '):
            continue
        elif line.startswith(PREFIXES['emoji']):
            if len(current_servers) == 0:
                raise ValueError(f'Line "{line}": emoji without server filter')

            emoji_search = line.removeprefix(PREFIXES['emoji'])

            if emoji_search.startswith(PREFIXES['include']):
                mode = Mode.INCLUDE
                emoji_search = emoji_search.removeprefix(PREFIXES['include'])
            elif emoji_search.startswith(PREFIXES['exclude']):
                mode = Mode.EXCLUDE
                emoji_search = emoji_search.removeprefix(PREFIXES['exclude'])
            else:
                raise ValueError(
                    f'Line "{line}": emoji must start with "+ " or "- "'
                )

            if specific_search := SPECIFIC_SEARCH.search(emoji_search):
                current_emojis = filter(
                    lambda emoji: emoji.name == specific_search.group(),
                    servers_emojis,
                )
            elif regex_search := REGEX_SEARCH.search(emoji_search):
                compiled: re.Pattern = re.compile(regex_search.group())
                current_emojis = filter(
                    lambda emoji: compiled.search(emoji.name),
                    emoji_data.emojis,
                )
            else:
                raise ValueError(f'Line "{line}": invalid server search')

            if mode == Mode.INCLUDE:
                emojis.update(current_emojis)
            else:
                emojis.difference_update(current_emojis)
        else:
            if line.startswith(PREFIXES['include']):
                mode = Mode.INCLUDE
                server_search = line.removeprefix(PREFIXES['include'])
            elif line.startswith(PREFIXES['exclude']):
                mode = Mode.EXCLUDE
                server_search = line.removeprefix(PREFIXES['exclude'])
            else:
                mode = Mode.PASSIVE
                server_search = line

            if ALL_SEARCH.search(server_search):
                current_servers = list(emoji_data.servers)
            elif (
                specific_search := SPECIFIC_SEARCH.search(server_search)
            ) and (specific_search.group() in emoji_data.servers):
                current_servers = [specific_search.group()]
            elif regex_search := REGEX_SEARCH.search(server_search):
                compiled: re.Pattern = re.compile(regex_search.group())
                current_servers = list(
                    filter(compiled.search, emoji_data.servers)
                )
            else:
                raise ValueError(f'Line "{line}": invalid server search')

            servers_emojis = filter(
                lambda emoji: emoji.server in current_servers,
                emoji_data.emojis,
            )
            if mode in (Mode.INCLUDE, Mode.EXCLUDE):
                if mode == Mode.INCLUDE:
                    emojis.update(servers_emojis)
                else:
                    emojis.difference_update(servers_emojis)

    return list(emojis)
