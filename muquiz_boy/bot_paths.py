from pathlib import Path
import pickle

import editor as ed
import ly_templates as lytemp

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


def user_session_savefile(userid, session_name):
    return SAVES / userid / f'{session_name}.pickle'


def user_load_session(userid, session_name):
    savefile = user_session_savefile(userid, session_name)
    if savefile.exists():
        with open(savefile, 'rb') as savefile:
            return pickle.load(savefile)
    else:
        return ed.LySessionSave(
            session_name,
            # TODO: Let user pick starting template
            lytemp.piano_template()
        )
