from telegram.ext import CommandHandler, ConversationHandler, MessageHandler
from telegram.ext.filters import Filters
import json
from pathlib import Path

# Game options
g_options = json.loads(
    Path('./assets/options.json').open(encoding='utf8').read()
)

# ConversationHandler states
RECV_ANS = range(1)

# Handler functions
def cancel_round(upd, ctx):
    return ConversationHandler.END

def start_round(upd, ctx):
    upd.message.reply_text('Hello')
    return ConversationHandler.END

def receive_ans(upd, ctx):
    return ConversationHandler.END

round_handler = ConversationHandler(
    entry_points=[
        CommandHandler('round', start_round)
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
