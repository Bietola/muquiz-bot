from dotty_dict import dotty
import abjad as abj


class LySessionSave:
    def __init__(self, score):
        self.score = score
        self.edit_list = []
        self.cur_edit = []


def apply_edit(cur_session, edit):
    sess = cur_session

    # NB. ignore all before mention of first command
    #     (can be used as kind of comment)
    for comm_section in edit.split(':')[1:]:
        command = comm_section.split()[0]
        args = comm_section.split('\n')[0].split()[1:]
        contents = '\n'.join(comm_section.split('\n')[1:])

        # DB
        # print(command, args, contents)

        # Edit
        if command == 'e':
            voice_path = args[0]

            sess.cur_edit = voice_path
            sess.edit_list = [voice_path]

        # Substitute
        elif command == 's':
            substitute_voice(sess.score, sess.cur_edit, contents)

        # Add instrument
        # TODO: Consider shorter version of `add` string?
        elif command == 'add':
            name = args[0]

            voice = abj.Voice('c', name='voice1')
            abj.attach(abj.Trumpet(), voice[0])

            staff = abj.Staff([voice], name=name)
            abj.attach(
                abj.LilyPondLiteral(r'\set Staff.midiInstrument = "trumpet"'),
                staff[0]
            )

            sess.score.append(staff)


def substitute_voice(score, voice_path, contents):
    to_edit = score
    for key in voice_path.split('/')[1:]:
        key = key.strip('\n')

        to_edit = to_edit[key]

    # TODO: DB
    # from pprint import pprint
    # print('printing contents')
    # pprint(contents)

    # TODO: Make specifying different voices possible
    abj.mutate.replace(
        to_edit['voice1'],
        # TODO: Find out why `str` is needed
        abj.Voice(str(contents), name='voice1'),
        # TODO: Find out why can't do this
        # wrappers=True
    )


#########
# TESTS #
#########


def test_sub_1_line_piano_left_hand():
    import sys
    import ly_utils as ly

    score = ly.piano_template(
        right='d4 g c',
        left='<g b d>4. <c e g>4'
    )

    print('showing score before edit')
    abj.show(score)
    next(sys.stdin)

    apply_edit(
        LySessionSave(score),
        ":e /piano/right\n"
        ":s\n"
        "\\relative c' { d4 g c }"
    )

    print('showing score after edit')
    abj.show(score)
