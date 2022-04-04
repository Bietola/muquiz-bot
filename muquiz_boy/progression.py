import random
import abjad as abj

import ly_utils as ly


LEVELS = {
    1: {
        'modes': [ly.MODES['major']],
        'tonics': [abj.NamedPitch('c')],
        'octaves': [abj.Octave(4)],
        'degrees': [1, 2, 3, 4],
        'notes_n': 1,
        'min_guesses': 10,
        'min_accuracy': 0.8
    },
    2: {
        'modes': [ly.MODES['major']],
        'tonics': [abj.NamedPitch('c')],
        'octaves': [abj.Octave(4)],
        'degrees': [5, 6, 7, 8],
        'notes_n': 1,
        'min_guesses': 10,
        'min_accuracy': 0.8
    },
    3: {
        'modes': [ly.MODES['major']],
        'tonics': [abj.NamedPitch('c')],
        'octaves': [abj.Octave(4)],
        'degrees': [1, 2, 3, 4, 5, 6, 7, 8],
        'notes_n': 1,
        'min_guesses': 10,
        'min_accuracy': 0.8
    },
    4: {
        'modes': [ly.MODES['major']],
        'tonics': [abj.NamedPitch('c')],
        'octaves': [abj.Octave(4)],
        'degrees': [1, 2, 3, 4, 5, 6, 7, 8],
        'notes_n': 2,
        'min_guesses': 10,
        'min_accuracy': 0.8
    },
    5: {
        'modes': [ly.MODES['major']],
        'tonics': [abj.NamedPitch('g')],
        'octaves': [abj.Octave(4)],
        'degrees': [1, 2, 3, 4, 5, 6, 7, 8],
        'notes_n': 1,
        'min_guesses': 10,
        'min_accuracy': 0.8
    },
}


def get_lv(world, player):
    return LEVELS[
        world['players'][player]['level']
    ]


def gen_round_info(level) -> ([abj.Note], None):
    mode = random.choice(level['modes'])
    octave = random.choice(level['octaves'])
    tonic = random.choice(level['tonics'])
    degrees = level['degrees']

    scale = ly.make_scale(tonic, mode, octave, degrees)
    answer = abj.PitchSegment(
        random.choices(scale, k=level['notes_n'])
    )
    answer = [abj.Note(pitch, (1, 4)) for pitch in answer]

    jig = None # TODO

    return answer, jig
