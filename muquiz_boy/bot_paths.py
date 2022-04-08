from pathlib import Path

ROOT = Path(__file__).parent

DATA = ROOT / 'data'
ASSETS = DATA / 'assets'
TEMPLATES = ASSETS / 'templates'
GAME_DATA = DATA / 'game-data'

CACHE = DATA / 'cache'

SAVES = DATA / 'saves'


def user_current_ly(user):
    return SAVES / user / 'current.ly'
