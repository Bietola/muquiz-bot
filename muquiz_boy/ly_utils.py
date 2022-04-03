import bot_paths as paths
import os
from pathlib import Path
import re
import abjad as abj
import sys


MODES = {
    "major": abj.IntervalSegment("M2 M2 m2 M2 M2 M2 m2"),
    "minor": abj.IntervalSegment("M2 m2 M2 M2 m2 M2 M2"),
    "dorian": abj.IntervalSegment("M2 m2 M2 M2 M2 m2 M2"),
}


def make_scale(tonic, interval_segment, octave=4, degrees=range(1, 8)):
    pitches = []
    pitch = abj.NamedPitch(tonic)
    pitches.append(pitch)
    for i, interval in enumerate(interval_segment):
        if (i + 1) in degrees:
            pitch = pitch + interval
            pitches.append(pitch)
    pitch_segment = abj.PitchSegment(pitches)
    return pitch_segment


def lyfile_wrap(score, gen_midi=False):
    return abj.LilyPondFile([abj.Block(
        'score',
        [
            abj.Block('midi'),
            score
        ] if gen_midi else [score]
    )])


def ear_training_jig(key='c'):
    # TODO: Transpose to correct key

    score = abj.Score([abj.StaffGroup(
        [abj.Staff(
            [abj.Voice(
                r"\relative c { <c e g c>4 <f a d f> <g b d g> <c, e g c> }"
            )]
         ),
         abj.Staff(
            [abj.Voice(
                r"\relative c, { c4 f g c, }"
            )]
        )],
        lilypond_type='PianoStaff'
    )])

    return lyfile_wrap(score, gen_midi=True)


def midi2flac(midi_path, out=None):
    def err():
        print(f'ERR: Malformed midi file {midi_path}', file=sys.stderr)

    if isinstance(midi_path, Path):
        midi_str = str(midi_path.resolve())
        midi_path = midi_path
    elif isinstance(midi_path, str):
        midi_str = midi_path
        midi_path = Path(midi_str)
    else:
        print(f'ERR: argument type not supported {type(midi_path)}', file=sys.stderr)
        sys.exit(1)

    if m := re.compile(r'^([^\.]*)\.(midi|mid)$').match(midi_str):
        default_out = Path(m.group(1) + '.flac')
    else:
        err()
        return

    if not out:
        out = default_out

    from midi2audio import FluidSynth
    FluidSynth().midi_to_audio(midi_path, out)

    return out


def make_lilypond_expr(expr, language='english', relative_note='c'):
    old_path = Path.cwd()
    os.chdir(paths.CACHE)

    ly_path = Path('out.ly').resolve()

    with open(ly_path, 'w') as f:
        print(
            (paths.TEMPLATES / 'single_piano.ly').open(encoding='utf8').read().format(
                language=language,
                relative_note=relative_note,
                notes_to_play=expr
            ),
            file=f
        )

    os.system(f'lilypond {ly_path}')

    pdf_path = Path('out.pdf').resolve()
    midi_path = Path('out.midi').resolve()

    os.chdir(old_path)
    return pdf_path, midi_path, ly_path


def add_midi_to_abjad_output(raw):
    fixed_score_wrapper = '\n'.join(
        [r'\score {'] + raw.split('\n')[2:-1] + [r'}']
    )
    fixed_midi = fixed_score_wrapper.replace(r'\new midi', r'\midi')

    return fixed_midi
