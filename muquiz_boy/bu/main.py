import fire
from telegram.ext import Updater
from telegram.ext import CommandHandler
from pathlib import Path

import utils
import register
# TODO/CC
from register import RegChats

import muquiz_boy

####################
# Global Variables #
####################

# None for now

##################################
# Helper Functions ans Constants #
##################################

def cur_time():
    return time.strftime("%H:%M:%S", time.localtime())

########
# Main #
########

def main(max_spam_lv=1):
    # Basic logging functions
    def log(txt, silent=False, notify=True, spam_lv=1):
        print(f'main_thread: {txt}')

        if spam_lv <= max_spam_lv and not silent:
            regchats = RegChats.get()

            for chat_id in RegChats.get():
                updater.bot.send_message(
                    chat_id = chat_id,
                    text = txt,
                    disable_notification = not notify
                )

    ################################
    # Get access to bot with token #
    ################################

    utils.wait_until_connected(delay=20, trace=True)
    updater = Updater(
        token=(Path(__file__).parent.resolve() / 'token').read_text().strip(),
        use_context=True
    )
    dispatcher = updater.dispatcher


    #############
    # Bot Intro #
    #############

    # log('FirstBoy is awake')

    ############
    # Handlers #
    ############

    dispatcher.add_handler(
        CommandHandler(
            'register',
            register.handler
        )
    )

    dispatcher.add_handler(
        CommandHandler(
            'regcommit',
            register.commit
        )
    )

    dispatcher.add_handler(
        CommandHandler(
            'insult',
            lambda upd, ctx: ctx.bot.send_message(
                chat_id = upd.effective_chat.id,
                text = "no u"
            )
        )
    )

    dispatcher.add_handler(muquiz_boy.round_handler)

    ###################
    # Start Things Up #
    ###################

    # Start bot
    updater.start_polling()

###############
# Entry Point #
###############

def cli():
    fire.Fire(main)

if __name__ == '__main__':
    cli()
