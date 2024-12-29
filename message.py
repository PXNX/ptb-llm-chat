from telegram import Update
from telegram.ext import CallbackContext


import anthropic

from config import OPENAPI

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=OPENAPI,
)
message = client.messages.create(
    model="laude-3-5-sonnet-20241022",
    max_tokens=256,
    messages=[
        {"role": "system", "content": "The user's name is Ghazal. She is a young syrian woman who needs your assistance to study Linguistics at university."}
    ]
)


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Heya! Just chat with me.")


async def handle_message(update: Update, context: CallbackContext):
    response = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": update.message.text,
            },
        ],

    )

    await update.message.reply_text(response.content)
