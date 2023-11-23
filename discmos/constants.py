import re
from enum import Enum

Mode = Enum('Mode', ['INCLUDE', 'EXCLUDE', 'PASSIVE'])
PREFIXES = {'include': '+ ', 'exclude': '- ', 'emoji': '    '}
SPECIFIC_SEARCH = re.compile(r'(?<=").*(?=")')
REGEX_SEARCH = re.compile(r'(?<=^/).*(?=/$)')

EMOJI_URL = (
    'https://cdn.discordapp.com/emojis/{ID}.webp?size=96&quality=lossless'
)
EMOJI_FILE = '{ID}.png'

SIZE = (96, 96)
BACKGROUND_COLOR = (49, 51, 56)

DISCORD_URL = 'https://discord.com/app'
