from pathlib import Path

ROOT = Path(__file__).parent

DATA = ROOT / 'data'
ASSETS = DATA / 'assets'
TEMPLATES = ASSETS / 'templates'
GAME_DATA = DATA / 'game-data'

CACHE = DATA / 'cache'

SAVES = DATA / 'saves'

SOUNDFONTS = ASSETS / 'soundfonts'
DEFAULT_SOUNDFONT = SOUNDFONTS / 'SGM-V2.sf2'
# DEFAULT_SOUNDFONT = SOUNDFONTS / 'FluidR3_GM.sf2'


def user_session_savefile(user):
    return SAVES / user / 'current.pickle'
