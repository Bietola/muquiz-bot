import bot_paths as paths
import os
from pathlib import Path

def expr_to_file(expr, language='english', relative_note='c'):
    old_path = Path.cwd()
    os.chdir(paths.CACHE)

    with open('to_play.ly', 'w') as f:
        print(
            (paths.TEMPLATES / 'single_piano.ly').open(encoding='utf8').read().format(
                language=language,
                relative_note=relative_note,
                notes_to_play=expr
            ),
            file=f
        )

    os.system('lilypond to_play.ly')

    from midi2audio import FluidSynth
    FluidSynth().midi_to_audio('to_play.midi', 'to_play.flac')

    ret = Path('to_play.flac')
    os.chdir(old_path)
    return ret
