import json
from pathlib import Path
from typing import List

import dacite

from .classes import Emoji, EmojiData
from .filter_emojis import filter_emojis


def get_emoji_data(workspace: Path) -> EmojiData:
    emoji_data_text = workspace.joinpath('emoji-data.json').read_text()
    emoji_data_dict = json.loads(emoji_data_text)
    emoji_data = dacite.from_dict(
        EmojiData, emoji_data_dict, dacite.Config(cast=[set, int])
    )
    return emoji_data


def emojis_from_workspace(workspace: Path) -> List[Emoji]:
    emoji_data = get_emoji_data(workspace)
    include = Path(workspace, 'include.txt').read_text()
    emojis = filter_emojis(emoji_data, include)
    return emojis
