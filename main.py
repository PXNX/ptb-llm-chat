import logging
from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
from datetime import datetime
from os import makedirs, path
from sys import platform, version_info
from typing import Final

from telegram import LinkPreviewOptions
from telegram.constants import ParseMode
from telegram.ext import MessageHandler, Defaults, ApplicationBuilder, filters, CommandHandler, PicklePersistence, \
    Application

from config import TOKEN, ADMINS, LLM_PATH

from message import start, handle_message


def add_logging():
    log_filename: Final[str] = rf"./logs/{datetime.now().strftime('%Y-%m-%d/%H-%M-%S')}.log"
    makedirs(path.dirname(log_filename), exist_ok=True)
    logging.basicConfig(
        format="%(asctime)s %(levelname)-5s %(funcName)-20s [%(filename)s:%(lineno)d]: %(message)s",
        encoding="utf-8",
        filename=log_filename,
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


if __name__ == "__main__":

   # add_logging()




    if version_info >= (3, 8) and platform.lower().startswith("win"):
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    app = (ApplicationBuilder().token(TOKEN)
           .defaults(Defaults(parse_mode=ParseMode.HTML, link_preview_options=LinkPreviewOptions(is_disabled=True)))
           .persistence(PicklePersistence(filepath="persistence"))
           .read_timeout(50).get_updates_read_timeout(50)
           .build())


    app.add_handler(CommandHandler("start", start,filters.ChatType.PRIVATE))# & filters.Chat(ADMINS)))

    app.add_handler(MessageHandler(  filters.ChatType.PRIVATE &filters.TEXT, handle_message)) # filters.Chat(ADMINS) &


    # Commands have to be added above
    #  app.add_error_handler( report_error)  # comment this one out for full stacktrace

    print("### RUNNING LOCAL ###")
    app.run_polling(poll_interval=1, drop_pending_updates=False)
