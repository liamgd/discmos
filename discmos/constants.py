import re
from enum import Enum

Mode = Enum('Mode', ['INCLUDE', 'EXCLUDE', 'PASSIVE'])
PREFIXES = {'include': '+ ', 'exclude': '- ', 'emoji': '    '}
ALL_SEARCH = re.compile(r'(?<=^)all(?=( *// .*)?$)')
SPECIFIC_SEARCH = re.compile(r'(?<=^").*(?="( *// .*)?$)')
REGEX_SEARCH = re.compile(r'(?<=^/).*(?=/( *// .*)?$)')

DEFAULT_INCLUDE = '''+ all
// Replace with "- all" to include no emojis by default
// Use + "<server name>" or - "<server name>" to include or exclude servers
'''

EMOJI_URL = (
    'https://cdn.discordapp.com/emojis/{ID}.webp?size=96&quality=lossless'
)
EMOJI_FILE = '{ID}.png'

SIZE = (96, 96)
BACKGROUND_COLOR = (49, 51, 56)

DISCORD_URL = 'https://discord.com/app'
