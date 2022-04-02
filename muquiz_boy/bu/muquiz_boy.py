from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext.filters import Filters
from collections import defaultdict
import json
from pathlib import Path
import os
import shutil
import random

import bot_paths as paths
from ly_utils import *

# Game options
g_options = json.loads(
    (paths.ASSETS / 'options.json').open(encoding='utf8').read()
)

# Game state
g_game = {
    'INIT_PRIZE': 10,
    'ALL_NOTES': ['c', 'd', 'e', 'f', 'g'],

    'players': defaultdict(
        lambda: {
            'points': 0,
            'active': False,
            'attempts': 0
        },
        json.loads((paths.ASSETS / 'players.json').open(encoding='utf8').read())
    ),

    'round': {
        'answer': 'c',
        'messages_to_del': []
    }
}

# ConversationHandler states
RECV_ANS, MKLOOP = range(2)

def save_game(field=None):
    global g_game

    (paths.ASSETS / 'players.json').write_text(
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
    msg_to_del = g_game['round']['messages_to_del']

    old_dir = Path().cwd()
    os.chdir(paths.CACHE)

    reset_attempts()

    # Generate and send jig
    # TODO: Handle transposition
    shutil.copy(paths.TEMPLATES / 'c_jig.ly', './jig.ly')
    os.system('lilypond jig.ly')

    audio_path = midi2flac('jig.midi')

    # from pydub import AudioSegment
    # AudioSegment.from_file(
    #     'jig.flac', format='flac'
    # ).export(
    #     'jig.mp3', format='mp3'
    # )

    msg_to_del.append(
        upd.message.reply_audio(
            open(audio_path, 'rb'),
            caption=f'Prize: {g_game["INIT_PRIZE"]}'
        )
    )
    
    # Pick and send note(s) to guess
    # TODO: Handle multiple notes
    # TODO: Handle other scales
    answer = random.choice(g_game['ALL_NOTES'])
    g_game['round']['answer'] = answer

    msg_to_del.append(upd.message.reply_audio(
        open(
            midi2flac(make_lilypond_expr(answer)[1]),
            'rb'
        ),
        caption='Guess this note'
    ))

    os.chdir(old_dir)
    return RECV_ANS


def receive_ans(upd, ctx):
    global g_game
    msg_to_del = g_game['round']['messages_to_del']
    players = g_game['players']
    user = upd.message.from_user.username

    prize = g_game['INIT_PRIZE'] / (2 ** players[user]['attempts'])

    msg_to_del.append(upd.message)

    if upd.message.text.lower() == g_game['round']['answer']:
        upd.message.reply_text(f'Ye, {user} gets +{prize}')
        players[user]['points'] += prize

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
            players,
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

    pdf_path, midi_path = make_lilypond_expr(to_execute)

    upd.message.reply_audio(
        open(midi2flac(midi_path), 'rb')
    )
    upd.message.reply_document(
        open(pdf_path, 'rb')
    )

    return ConversationHandler.END


def mkloop(upd, ctx):
    user = upd.message.from_user.username
    current_ly = g_game['players'][user]['saves']['current']

    # TODO: Err not text
    expr = upd.message.text

    upd.message.reply_text('Compiling lilypond...')

    if expr == '/stop':
        return ConversationHandler.END
    elif m := re.compile(r'^/tr\s+(\w+)\s+(\w+)\s*$').match(expr):
        frm = m.group(1)
        to = m.group(2)

        ly.music.document(
            ly.document.Document(current_ly)
        )

        current_ly = ly.transpose(current_ly, frm, to)

        # TODO: upd.message.reply_text(ly_extract_expr(current_ly))
        upd.message.reply_text(current_ly)
        # ly_make_send(current_ly)

        return MKLOOP

    # TODO: Wrap in ly_make_send
    pdf_path, midi_path, ly_path = make_lilypond_expr(
        expr,
        relative_note='c\''
        # language=''
    )

    shutil.copy(ly_path, paths.CURRENT_LY)

    upd.message.reply_audio(
        open(midi2flac(midi_path), 'rb')
    )
    upd.message.reply_document(
        open(pdf_path, 'rb')
    )

    return MKLOOP


round_handler = ConversationHandler(
    entry_points=[
        CommandHandler('mk', mk_reply),
        CommandHandler('mklp', lambda _1, _2: MKLOOP),

        CommandHandler('qz', start_round),
        CommandHandler('rank', send_rank)
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
