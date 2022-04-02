import bot_paths as paths
import os
from pathlib import Path
import re


def midi2flac(midi_path, out=None):
    def err():
        print(f'ERR: Malformed midi file {midi_path}', file=os.stderr)

    if isinstance(midi_path, str):
        midi_str = midi_path
        midi_path = Path(midi_str)
    elif isinstance(midi_path, Path):
        midi_str = str(midi_path.resolve())
        midi_path = midi_path

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
