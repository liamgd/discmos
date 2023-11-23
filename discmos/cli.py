import io
import webbrowser
from pathlib import Path
from typing import Any, List

import click
import pyclip
import win32clipboard
from PIL import Image

from .classes import Emoji
from .constants import DEFAULT_INCLUDE, DISCORD_URL
from .download import download_emojis
from .emoji_data import emojis_from_workspace
from .mosaic import run_composite, run_mosaic

DOCS = {
    'workspace': 'Path to the desired workspace directory (does not have to exist)',
    'update': 'Forcibly update emoji image files, even if they already exist',
}


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
    '''
    Initializes the provided path to be a directory that will serve as
    a workspace for the use of this tool.

    WORKSPACE: Path to the desired workspace directory (does not have to exist)
    '''
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
        include_file.write_text(DEFAULT_INCLUDE)
    click.echo(f'Initialized {workspace}')


@cli.command()
@click.argument(
    'workspace',
    type=click.Path(
        file_okay=False, writable=True, resolve_path=True, path_type=Path
    ),
)
def preview_include(workspace: str) -> None:
    '''
    Prints which emojis will be included given include.txt and
    emoji-data.json in the workspace directory.

    WORKSPACE: Path to the desired workspace directory (does not have to exist)
    '''
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
@click.option(
    '--update', type=bool, is_flag=True, default=False, help=DOCS['update']
)
def download_all(workspace: Path, update: bool) -> None:
    '''
    Downloads all of the emojis from emoji-data.json that are included
    in include.txt.

    WORKSPACE: Path to the desired workspace directory (does not have to exist)
    UPDATE: Forcibly update emoji image files, even if they already exist
    '''
    emojis = emojis_from_workspace(workspace)

    download_emojis(emojis, workspace.joinpath('emojis'), update)


@cli.command()
def scrape() -> None:
    '''
    Allows the javascript console script to be copied to the clipboard
    and the Discord website app to be opened in a new tab.
    '''
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

    click.echo(
        '''
Steps to scrape emojis:
1. Ensure that you have initialized a workspace directory with discmos
   init-workspace prior to scraping emojis.
2. Copy the javascript console script (console.js on github.com).
3. Open the Discord website app in the browser and navigate to a server
   or direct message where you can type a message.
4. Open the inspect element on the website (control-shift-C or
   command-option-C).
5. Navigate to the console pane in the inspect element.
6. Paste the javascript console script and press enter to initiate it.
   Until done, do not press any key on the keyboard.
7. Click to open the emoji pane to the right of the text input bar on
   the bottom of the screen.
8. Scroll up and down in the emoji pane until all custom server emojis
   have appeared at least once (emoji names should appear in the
   console).
9. Press any key on the keyboard (ex. space) or type "save()" in the
   console.
10. Save emoji-data.json in the workspace directory.
11. You are done, and you can close the Discord tab.
'''
    )


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
@click.option(
    '--suffix',
    type=str,
    default='_mosaic_{we}_{r}_{hw}_{sw}_{vw}',
    help='Text added to the stem of the source file name to form the output file name',
)
@click.option(
    '--hue-weight',
    type=float,
    default=1,
    help='How much hue should be preserved',
)
@click.option(
    '--saturation-weight',
    type=float,
    default=1,
    help='How much saturation should be preserved',
)
@click.option(
    '--value-weight',
    type=float,
    default=1,
    help='How much value should be preserved',
)
@click.option(
    '--save',
    type=bool,
    default=False,
    is_flag=True,
    help='Whether to save the output to a file',
)
@click.option(
    '--show',
    type=bool,
    default=False,
    is_flag=True,
    help='Whether to display the output',
)
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
    '''
    Runs the mosaic algorithm.

    WORKSPACE: Path to the desired workspace directory (does not have to exist)
    SOURCE: The name of the source file in <workspace>/sources/
    WIDTH-EMOJIS: The width of the final mosaic in emojis (not pixels, lower is faster; start with 10 to 80)
    RESIZE: The width and height that each tile is resized to before computation (lower is faster and uses less memory; start with 4 to 16)
    '''
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
    '''
    Show and save the emoji text to put into Discord.
    '''
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
    '''
    Show and save a composite image of how the emojis would be rendered
    (useful to get around the Discord character limit).

    RESIZE-WIDTH: Width in pixels to resize the final image to (aspect ratio retained; start with 200 to 2000)
    '''
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
