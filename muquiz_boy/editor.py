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

        # Edit
        if command == 'e':
            voice_path = args[0]

            sess.cur_edit = voice_path
            sess.edit_list = [voice_path]

        # Substitute
        elif command == 's':
            substitute_voice(sess.score, sess.cur_edit, contents)


def substitute_voice(score, voice_path, contents):
    abj.mutate.replace(
        dotty(score)[voice_path.replace('/', '.')],
        contents
    )


#########
# TESTS #
#########


def 
