import abjad as abj


# TODO: Add other templates
# START_TEMPLATES = {
#     'piano': piano_template()
# }


def opt_voice(notes=None, name='voice1'):
    return abj.Voice(notes, name=name) if notes else abj.Voice(name=name)


# TODO: Find way to generate with no notes
def piano_template(right=None, left=None):
    piano = abj.StaffGroup(
        [
            abj.Staff(
                [opt_voice(right, name='voice1')],
                name='right'
            ),
            abj.Staff(
                [opt_voice(left, name='voice1')],
                name='left'
            )
        ],
        lilypond_type='PianoStaff',
        name='piano'
    )

    score = abj.Score([piano], name='score')

    return score
