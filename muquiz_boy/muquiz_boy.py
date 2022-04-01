from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext.filters import Filters
from collections import defaultdict
import json
from pathlib import Path
import os
import shutil
import random

import bot_paths as paths
import ly_utils

# Game options
g_options = json.loads(
    (paths.ASSETS / 'options.json').open(encoding='utf8').read()
)

# Game state
g_game = {
    'INIT_PRIZE': 10,
    'ALL_NOTES': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],

    'players': defaultdict(
        lambda: {
            'points': 0,
            'active': False,
            'attempts': 0
        },
        json.loads(Path('./assets/players.json').open(encoding='utf8').read())
    ),

    'round': {
        'answer': 'c',
        'messages_to_del': []
    }
}

# ConversationHandler states
RECV_ANS = range(1)

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

    from midi2audio import FluidSynth
    FluidSynth().midi_to_audio('jig.midi', 'jig.flac')

    # from pydub import AudioSegment
    # AudioSegment.from_file(
    #     'jig.flac', format='flac'
    # ).export(
    #     'jig.mp3', format='mp3'
    # )

    msg_to_del.append(
        upd.message.reply_audio(
            open('jig.flac', 'rb'),
            caption=f'Prize: {g_game["INIT_PRIZE"]}'
        )
    )
    
    # Pick and send note(s) to guess
    # TODO: Handle multiple notes
    # TODO: Handle other scales
    answer = random.choice(g_game['ALL_NOTES'])
    g_game['round']['answer'] = answer

    msg_to_del.append(upd.message.reply_audio(
        open(ly_utils.expr_to_file(answer), 'rb'),
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

round_handler = ConversationHandler(
    entry_points=[
        CommandHandler('go', start_round),
        CommandHandler('rank', send_rank)
    ],
    states={
        RECV_ANS: [MessageHandler(Filters.text, receive_ans)],
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
