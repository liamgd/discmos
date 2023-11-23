import io
import webbrowser
from pathlib import Path
from typing import Any, List

import click
import pyclip
import win32clipboard
from PIL import Image

from .classes import Emoji
from .constants import DISCORD_URL
from .download import download_emojis
from .emoji_data import emojis_from_workspace
from .mosaic import run_composite, run_mosaic


def copy_data(clipboard_format: int, data: Any) -> None:
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clipboard_format, data)
    finally:
        win32clipboard.CloseClipboard()


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument(
    'workspace',
    type=click.Path(
        file_okay=False, writable=True, resolve_path=True, path_type=Path
    ),
)
def init_workspace(workspace: Path) -> None:
    emojis_dir = workspace.joinpath('emojis')
    sources_dir = workspace.joinpath('sources')
    output_images_dir = workspace.joinpath('output-images')
    output_text_dir = workspace.joinpath('output-text')
    include_file = workspace.joinpath('include.txt')
    if not workspace.is_dir():
        workspace.mkdir()
    if not emojis_dir.is_dir():
        emojis_dir.mkdir()
    if not sources_dir.is_dir():
        sources_dir.mkdir()
    if not output_images_dir.is_dir():
        output_images_dir.mkdir()
    if not output_text_dir.is_dir():
        output_text_dir.mkdir()
    if not include_file.is_file():
        include_file.write_text('+ all\n')
    click.echo(f'Initialized {workspace}')


@cli.command()
@click.argument(
    'workspace',
    type=click.Path(
        file_okay=False, writable=True, resolve_path=True, path_type=Path
    ),
)
def preview_include(workspace: str) -> None:
    emojis = emojis_from_workspace(workspace)

    for emoji in emojis:
        print(f'Emoji :{emoji.name}: from server "{emoji.server}"')


@cli.command()
@click.argument(
    'workspace',
    type=click.Path(
        file_okay=False, writable=True, resolve_path=True, path_type=Path
    ),
)
@click.option('--update', type=bool, is_flag=True, default=False)
def download_all(workspace: Path, update: bool) -> None:
    emojis = emojis_from_workspace(workspace)

    download_emojis(emojis, workspace.joinpath('emojis'), update)


@cli.command()
def scrape() -> None:
    response: str = click.prompt(
        f'Copy javascript console script to clipboard? y/n'
    )
    if response.lower() == 'y':
        script_path = Path(__file__).parent.parent.joinpath('console.js')
        print(script_path)
        with open(script_path, 'r') as file:
            script = file.read()
        pyclip.copy(script)
        click.echo('Copied script')

    response: str = click.prompt(f'Open {DISCORD_URL}? y/n')
    if response.lower() == 'y':
        webbrowser.open(DISCORD_URL)
        click.echo(f'Opened {DISCORD_URL}')


@cli.group()
@click.argument(
    'workspace',
    type=click.Path(
        file_okay=False, writable=True, resolve_path=True, path_type=Path
    ),
)
@click.argument('source', type=str)
@click.argument('width-emojis', type=int)
@click.argument('resize', type=int)
@click.option('--suffix', type=str, default='_mosaic_{we}_{r}_{hw}_{sw}_{vw}')
@click.option('--hue-weight', type=float, default=1)
@click.option('--saturation-weight', type=float, default=1)
@click.option('--value-weight', type=float, default=1)
@click.option('--save', type=bool, default=False, is_flag=True)
@click.option('--show', type=bool, default=False, is_flag=True)
@click.pass_context
def mosaic(
    ctx: click.Context,
    workspace: Path,
    source: str,
    width_emojis: int,
    resize: int,
    suffix: str,
    hue_weight: float,
    saturation_weight: float,
    value_weight: float,
    save: bool,
    show: bool,
) -> None:
    emojis = emojis_from_workspace(workspace)

    output_emojis = run_mosaic(
        emojis,
        workspace.joinpath('emojis'),
        workspace.joinpath('sources', source),
        width_emojis,
        (resize, resize),
        Image.LANCZOS,
        hue_weight,
        saturation_weight,
        value_weight,
    )

    ctx.ensure_object(dict)
    ctx.obj['emojis'] = output_emojis
    ctx.obj['workspace'] = workspace
    ctx.obj['source'] = source
    ctx.obj['suffix'] = suffix.format(
        we=width_emojis,
        r=resize,
        hw=hue_weight,
        sw=saturation_weight,
        vw=value_weight,
    )
    ctx.obj['save'] = save
    ctx.obj['show'] = show


@mosaic.command()
@click.pass_context
def text(ctx: click.Context) -> None:
    output_emojis: List[List[Emoji]] = ctx.obj['emojis']
    workspace: Path = ctx.obj['workspace']
    source: str = ctx.obj['source']
    suffix: str = ctx.obj['suffix']
    save: bool = ctx.obj['save']
    show: bool = ctx.obj['show']

    output_text = ''
    for row in output_emojis:
        for emoji in row:
            output_text += f':{emoji.name}: '
        output_text.removesuffix(' ')
        output_text += '\n'

    pyclip.copy(output_text)
    click.echo('Copied emojis to clipboard')

    if save:
        save_path = workspace.joinpath(
            'output-text', f'{Path(source).stem}{suffix}.txt'
        )
        with open(save_path, 'w') as file:
            file.write(output_text)
        click.echo(f'Saved emojis to {save_path}')

    if show:
        click.echo(output_text)


@mosaic.command()
@click.argument('resize-width', type=int)
@click.pass_context
def composite(ctx: click.Context, resize_width: int) -> None:
    output_emojis: List[List[Emoji]] = ctx.obj['emojis']
    workspace: Path = ctx.obj['workspace']
    source: str = ctx.obj['source']
    suffix: str = ctx.obj['suffix']
    save: bool = ctx.obj['save']
    show: bool = ctx.obj['show']

    image = run_composite(output_emojis, workspace.joinpath('emojis'))
    image = image.resize(
        (resize_width, round(image.height / image.width * resize_width)),
        Image.LANCZOS,
    )

    image_bytes = io.BytesIO()
    image.save(image_bytes, 'DIB')
    copy_data(win32clipboard.CF_DIB, image_bytes.getvalue())
    click.echo('Copied composite image to clipboard')

    if save:
        save_path = workspace.joinpath(
            'output-images', f'{Path(source).stem}{suffix}.png'
        )
        with open(save_path, 'wb') as file:
            image.save(file)
        click.echo(f'Saved emojis to {save_path}')

    if show:
        image.show()
