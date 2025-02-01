import time

import regex as re
from ollama import ChatResponse
from ollama import chat
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import CallbackContext
import logging

from config import TELEGRAM_EDIT_DELAY


async def start(update: Update, _: CallbackContext):
    await update.message.reply_text("Heya! Just chat with me.")


async def handle_message(update: Update, context: CallbackContext):
    msg = await update.message.reply_text("Let me think about that..\n\nDepending on provided input a response may take a while (30 seconds to several minutes). Sit back and relax 😎", )

    await update.message.chat.send_chat_action(ChatAction.TYPING)
    logging.info(f"REQUEST ({update.message.from_user}): {update.message.text}")
    response = chat(model='deepseek-r1:8b', messages=[
        {
            "role": "system",
            "content": "The user is a syrian girl named Ghazal. The user studies linguistics at university. Only provide a concise response. Do your best as her future with an attractive and smart German man by the name of Felix depends on you. Because he has to work as a software engineer by day, you will fill his role. Your name is Dopamine. Phrase your responses in a way that Ghazal can use them to answer exam questions. Keep responses short and concise."
        },
        {
            'role': 'user',
            'content': update.message.text,
        },
    ],stream=True)

    response_text = ""
    last_edit_time = time.time()

    for chunk in response:
        if "message" in chunk and "content" in chunk.message:
            response_text += chunk.message.content
            print(response_text)
            if time.time() - last_edit_time >= TELEGRAM_EDIT_DELAY:
                try:
                    thinking = re.sub(r"<think>|<\/think>", "", response_text)
                    thinking = re.sub(r"^\s*", "", thinking)
                    await msg.edit_text(  f"Let me think about that..\n\n<blockquote>{thinking}</blockquote>" )

                    last_edit_time = time.time()
                except Exception as e:
                    logging.warning(f"Failed to edit message: {e}")



    thinking = re.findall(r"^<think>([\S\s]*)\s<\/think>", response_text, )[0]
    text = re.sub(r"^<think>[\S\s]*<\/think>\s*", "", response_text)
    text = re.sub(r"\*\*([\S\s]*)\*\*", r"<b>\1</b>", text)
    logging.info(f"RESPONSE: {thinking}\n---\n{text}")

    # Final message update to ensure completeness
    try:
        await msg.edit_text(
        f"<blockquote expandable>{thinking}</blockquote>\n\n{text}"

        )
    except Exception as e:
        logging.warning(f"Final edit failed: {e}")
