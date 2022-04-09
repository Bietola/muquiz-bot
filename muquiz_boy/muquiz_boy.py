from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext.filters import Filters
from collections import defaultdict
import json
from pathlib import Path
import os
import abjad as abj
from pprint import pformat
from lenses import bind
from numbers import Number
import shutil

import progression as prog
import bot_paths as paths
import ly_utils as ly

# Game state
g_game = {
    'INIT_PRIZE': 3,
    'ALL_NOTES': ['c', 'd', 'e', 'f', 'g'],

    'players': defaultdict(
        lambda: {
            'points': 0,
            'active': False,
            'attempts': 0,
            'guesses': 0,
            'accuracy': 0
        },
        json.loads((paths.GAME_DATA / 'players.json').open(encoding='utf8').read())
    ),

    'round': {
        'answer': prog.gen_round_info(prog.LEVELS[1]),
        'messages_to_del': []
    }
}

# ConversationHandler states
RECV_ANS, MKLOOP = range(2)

def save_game(field=None):
    global g_game

    (paths.GAME_DATA / 'players.json').write_text(
        json.dumps(g_game['players'], indent=4),
        encoding='utf-8'
    )

def reset_attempts():
    global g_game

    for pl in g_game['players'].values():
        pl['attempts'] = 0

# Handler functions
def cancel_round(upd, ctx):
    return ConversationHandler.END


def start_round(upd, ctx):
    global g_game

    user = upd.message.from_user.username
    level = prog.get_lv(g_game, user)
    msg_to_del = g_game['round']['messages_to_del']

    old_dir = Path().cwd()
    os.chdir(paths.CACHE)

    reset_attempts()

    # Generate and send jig
    # TODO: Handle transposition
    # shutil.copy(paths.TEMPLATES / 'c_jig.ly', './jig.ly')

    # os.system('lilypond jig.ly')
    os.system('rm -f *.midi')
    abj.persist.as_midi(
        ly.ear_training_jig(),
        'jig.midi'
    )

    audio_path = ly.midi2flac('jig.midi')

    # from pydub import AudioSegment
    # AudioSegment.from_file(
    #     'jig.flac', format='flac'
    # ).export(
    #     'jig.mp3', format='mp3'
    # )

    msg_to_del.append(
        upd.message.reply_audio(
            open(audio_path, 'rb')
        )
    )

    # Pick and send note(s) to guess
    # TODO: Handle multiple notes
    # TODO: Handle other scales
    # TODO: Handle jig
    answer, _jig = prog.gen_round_info(level)
    # TODO/CC: Find a way to convert this to simple string (e.g. 'c ds e') and test if it matches guess in msg form
    g_game['round']['answer'] = answer

    msg_to_del.append(upd.message.reply_audio(
        ly.midi2flac(
            abj.persist.as_midi(
                ly.lyfile_wrap(
                    abj.Score([abj.Voice(answer)]),
                    gen_midi=True
                ),
                'answer.midi'
            )[0]
        ).open('rb'),
        caption=f'Guess this tune (prize: {g_game["INIT_PRIZE"]})'
    ))

    os.chdir(old_dir)
    return RECV_ANS


def receive_ans(upd, ctx):
    global g_game
    msg_to_del = g_game['round']['messages_to_del']
    players = g_game['players']
    user = upd.message.from_user.username

    if upd.message.text[0] == '/':
        return RECV_ANS

    prize = g_game['INIT_PRIZE'] / (2 ** players[user]['attempts'])

    msg_to_del.append(upd.message)

    str_answer = [
        note.written_pitch.get_name().lower()
        for note in g_game['round']['answer']
    ]

    # upd.message.reply_text(f'DB: {str_answer}')

    if upd.message.text.lower().split() == str_answer:
        pl = players[user]

        players[user]['points'] += prize

        if (prize == g_game['INIT_PRIZE']):
            right_first_try = 1.5
        else:
            right_first_try = 0

        pl['accuracy'] = ((pl['accuracy'] * pl['guesses']) + right_first_try) / (pl['guesses'] + 1)
        pl['guesses'] += 1

        upd.message.reply_text(
            f'Ye, {user} gets +{prize} ({pl["guesses"]}/{round(pl["accuracy"], 2)})'
        )

        lv = prog.get_lv(g_game, user)
        if pl['guesses'] >= lv['min_guesses'] and pl['accuracy'] >= lv['min_accuracy']:
            lv_up_prize = 10 * pl['level']

            pl['level'] += 1
            pl['accuracy'] = 0
            pl['guesses'] = 0
            pl['points'] += lv_up_prize

            upd.message.reply_text(
                f'{user} reached level {pl["level"]} and gets a +{lv_up_prize}points prize!\n'
                f'level {pl["level"]}:\n'
                f'{pformat(prog.get_lv(g_game, user))}'
            )

        for msg in msg_to_del:
            ctx.bot.delete_message(upd.effective_chat.id, msg.message_id)
        g_game['round']['messages_to_del'] = []

        save_game()

        return ConversationHandler.END

    else:
        msg_to_del.append(
            upd.message.reply_text(f'{user} is wrong (prize = {prize / 2})')
        )
        players[user]['attempts'] += 1

        return RECV_ANS


def send_rank(upd, ctx):
    global g_game
    players = g_game['players']

    upd.message.reply_text(
        json.dumps(
            bind(players).Recur(Number).modify(lambda x: round(x, 3)),
            indent=4
        )
    )

    return ConversationHandler.END


def mk_reply(upd, ctx):
    # TODO: Put errors here
    if not (reply := upd.message.reply_to_message):
        return

    if not (to_execute := reply.text):
        return

    pdf_path, midi_path = ly.make_lilypond_expr(to_execute)

    upd.message.reply_audio(
        open(ly.midi2flac(midi_path), 'rb')
    )
    upd.message.reply_document(
        open(pdf_path, 'rb')
    )

    return ConversationHandler.END


def mkloop(upd, ctx):
    global g_game

    user = upd.message.from_user.username
    # current_ly = g_game['players'][user]['saves']['current']

    # TODO: Err not text
    expr = upd.message.text

    if expr == '/stop':
        return ConversationHandler.END

    if expr[0] != ':':
        return MKLOOP

    expr = expr[1:]

    upd.message.reply_text('Compiling lilypond...')

    # ly_file = ly.lyfile_wrap(
    #     abj.Score([abj.Voice(expr)]),
    #     gen_midi=True
    # )
    session = g_game[user]['abjad_session']
    ly_file = ly.lyfile_wrap(
        session.score,
        gen_midi=True
    )

    # Create various files
    old_dir = Path().cwd()
    os.chdir(paths.CACHE)

    midi_path = abj.persist.as_midi(ly_file, 'current.midi')[0]
    pdf_path = abj.persist.as_pdf(ly_file, 'current.pdf')[0]
    ly_path = abj.persist.as_ly(ly_file, 'current.ly')[0]

    upd.message.reply_audio(
        open(ly.midi2flac(midi_path), 'rb')
    )
    upd.message.reply_document(
        open(pdf_path, 'rb')
    )

    os.chdir(old_dir)

    return MKLOOP


def game_query(init_args=None, setter=False, getter=True):
    def send(upd, ctx):
        global g_game

        q_result = g_game

        keys = init_args.split('.') if init_args else []
        keys = keys + (ctx.args[0].split('.') if len(ctx.args) > 0 else [])
        for key in keys:
            if key == '%':
                key = upd.message.from_user.username

            q_result = q_result[key]

        upd.message.reply_text(pformat(q_result))

    return send


round_handler = ConversationHandler(
    entry_points=[
        CommandHandler('mk', mk_reply),
        CommandHandler('mklp', lambda _1, _2: MKLOOP),

        CommandHandler('qz', start_round),
        CommandHandler('rank', send_rank),

        CommandHandler('q', game_query()),
        CommandHandler('qpl', game_query('players')),
        CommandHandler('qround', game_query('round')),
        CommandHandler('lv', game_query('players.%.level'))
    ],
    states={
        RECV_ANS: [MessageHandler(Filters.text, receive_ans)],
        MKLOOP: [MessageHandler(Filters.text, mkloop)]
        # HANDLE_WIN: [MessageHandler(Filters.photo, photo)]
        # LOCATION: [
        #     MessageHandler(Filters.location, location),
        #     CommandHandler('skip', skip_location),
        # ],
        # BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
    },
    fallbacks=[CommandHandler('cancel', cancel_round)],
    per_user=False,
)
