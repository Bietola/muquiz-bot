import abjad as abj


# TODO: Add other templates
START_TEMPLATES = {
    'piano': piano_template()
}


def piano_template(right='', left=''):
    piano = abj.StaffGroup(
        [
            abj.Staff(
                [abj.Voice(right, name='voice1')],
                name='right'
            ),
            abj.Staff(
                [abj.Voice(left, name='voice1')],
                name='left'
            )
        ],
        lilypond_type='PianoStaff',
        name='piano'
    )

    score = abj.Score([piano], name='score')

    return score
