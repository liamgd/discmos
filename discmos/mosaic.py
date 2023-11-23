import math
from pathlib import Path
from time import time
from typing import List, Tuple

import torch
from PIL import Image

from .classes import Emoji
from .constants import EMOJI_FILE, SIZE
from .image_tensor import image_to_tensor


def find_closest_tiles(
    match_tiles: torch.Tensor,
    source_tiles: torch.Tensor,
    channel_weights: torch.Tensor,
) -> torch.Tensor:
    return (
        (source_tiles[:, None, ...] - match_tiles[None, :, ...])
        .abs()
        .mul(channel_weights[None, None, :, None])
        .flatten(start_dim=2)
        .sum(2)
        .argmin(1)
    )


def run_mosaic(
    emojis: List[Emoji],
    images_path: Path,
    source_path: Path,
    width_emojis: int,
    resize: Tuple[int, int],
    resample: int,
    hue_weight: float,
    saturation_weight: float,
    value_weight: float,
) -> List[List[Emoji]]:
    device = torch.device('cuda')
    image_tensors = []

    for emoji in emojis:
        image_path = images_path.joinpath(EMOJI_FILE.format(ID=emoji.id))
        image = Image.open(image_path)
        resized_image = image.resize(resize, resample).convert('HSV')

        image_tensor = image_to_tensor(resized_image).type(torch.short)
        image_tensors.append(image_tensor)

    match_tiles: torch.Tensor = torch.stack(image_tensors).to(device)
    match_tiles = match_tiles.flatten(start_dim=2)

    source_image_full = Image.open(source_path).convert('RGBA')
    source_size = (
        width_emojis * resize[0],
        math.floor(
            source_image_full.height / source_image_full.width * width_emojis
        )
        * resize[1],
    )
    source_image = Image.new('RGBA', source_size)
    source_image.alpha_composite(
        source_image_full.resize(source_size, resample)
    )
    source_image = source_image.convert('HSV')
    source_images = [
        image_to_tensor(
            source_image.crop((x, y, x + resize[0], y + resize[1]))
        ).type(torch.short)
        for x in range(0, source_image.width, resize[0])
        for y in range(0, source_image.height, resize[1])
    ]

    source_tiles: torch.Tensor = torch.stack(source_images).to(device)
    source_tiles = source_tiles.flatten(start_dim=2)

    channel_weights_list = [hue_weight, saturation_weight, value_weight]
    channel_dtype = (
        torch.short
        if all(weight.is_integer() for weight in channel_weights_list)
        else torch.float32
    )

    channel_weights = torch.tensor(
        [hue_weight, saturation_weight, value_weight],
        dtype=channel_dtype,
        device=device,
    )

    closest_tiles = find_closest_tiles(
        match_tiles, source_tiles, channel_weights
    )

    output_emojis = [
        [emojis[index] for index in row]
        for row in closest_tiles.reshape((width_emojis, -1)).T.tolist()
    ]
    return output_emojis


def run_composite(
    emoji_rows: List[List[Emoji]], images_path: Path
) -> Image.Image:
    width = len(emoji_rows[0]) * SIZE[0]
    height = len(emoji_rows) * SIZE[1]
    composite_image = Image.new('RGB', (width, height))

    for row_index, row in enumerate(emoji_rows):
        for column_index, emoji in enumerate(row):
            image_path = images_path.joinpath(EMOJI_FILE.format(ID=emoji.id))
            image = Image.open(image_path)
            composite_image.paste(
                image, (column_index * SIZE[0], row_index * SIZE[1])
            )

    return composite_image
