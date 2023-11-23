import io
import multiprocessing
from pathlib import Path
from typing import List

import requests
from PIL import Image

from .classes import Emoji
from .constants import BACKGROUND_COLOR, EMOJI_FILE, EMOJI_URL, SIZE


def download_url(url: str, path: Path) -> None:
    response = requests.get(url)
    transparent_image = Image.open(io.BytesIO(response.content)).convert(
        'RGBA'
    )

    image_partial = Image.new('RGBA', transparent_image.size, BACKGROUND_COLOR)
    image_partial.alpha_composite(transparent_image)

    image = Image.new('RGB', SIZE, BACKGROUND_COLOR)
    paste_position = (
        (SIZE[0] - image_partial.width) // 2,
        (SIZE[1] - image_partial.height) // 2,
    )
    image.paste(image_partial, paste_position)

    image.save(path)


def download_emojis(
    emojis: List[Emoji], directory: Path, update: bool
) -> None:
    if not update:
        downloaded = set(directory.iterdir())
        emojis = list(
            filter(
                lambda emoji: EMOJI_FILE.format(ID=emoji.id) not in downloaded,
                emojis,
            )
        )
    download_arguments = (
        (
            EMOJI_URL.format(ID=emoji.id),
            directory.joinpath(EMOJI_FILE.format(ID=emoji.id)),
        )
        for emoji in emojis
    )
    with multiprocessing.Pool() as pool:
        pool.starmap(download_url, download_arguments)
