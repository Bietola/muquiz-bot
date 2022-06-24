from dotty_dict import dotty
import abjad as abj
import utils as utl


class LySessionSave:
    def __init__(self, score):
        self.score = score
        self.edit_list = []
        self.cur_edit = []
        self.tempo = 128


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
            instrument = args[1].replace('_', ' ')

            voice = abj.Voice('c', name='voice1')
            # TODO: Find out if attaching instrument is actually necessary
            # abj.attach(abj.Trumpet(), voice[0])

            staff = abj.Staff([voice], name=name)
            abj.setting(staff).midiInstrument = f'"{instrument}"'
            abj.setting(staff).instrumentName = f'"{instrument.title()}"'

            sess.score.append(staff)

        elif command == 'rem':
            voice_path = args[0]

            to_rem, parent = utl.dotted_access(
                sess.score,
                voice_path,
                separator='/',
                skip_first=True,
                also_get_parent=True
            )
            parent.remove(to_rem)

        elif command == 'tempo':
            tempo = args[0]

            sess.tempo = tempo


def substitute_voice(score, voice_path, contents):
    to_edit = utl.dotted_access(
        score,
        voice_path.strip('\n'),
        separator='/',
        skip_first=True
    )

    # TODO: DB
    # from pprint import pprint
    # print('printing contents')
    # pprint(contents)

    # TODO: Make specifying different voices possible
    new_voice = abj.Voice(str(contents), name='voice1'),
    abj.mutate.replace(
        to_edit['voice1'],
        # TODO: Find out why `str` is needed
        abj.Voice(contents, name='voice1'),
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
