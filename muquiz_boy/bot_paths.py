from pathlib import Path

ROOT = Path(__file__).parent

DATA = ROOT / 'data'
ASSETS = DATA / 'assets'
TEMPLATES = ASSETS / 'templates'
GAME_DATA = DATA / 'game-data'

CACHE = DATA / 'cache'

SAVES = DATA / 'saves'


def user_session_savefile(user):
    return SAVES / user / 'current.pickle'
