from asyncio import run
import asyncio

from langchain.chains.conversation.base import ConversationChain
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms.gpt4all import GPT4All
from langchain_core.prompts import PromptTemplate
from telegram import Update, Bot
from telegram.ext import CallbackContext


from config import LLM_PATH, ADMINS
from langchain_core.callbacks import BaseCallbackHandler


memory = ConversationBufferMemory()


class TelegramEditCallbackHandler(BaseCallbackHandler):
    def __init__(self, context, chat_id, message_id):
        self.context = context
        self.chat_id = chat_id
        self.message_id = message_id
        self.token_buffer = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called whenever a new token is generated."""
        self.token_buffer.append(token)

        # Edit the message after every 10 tokens
        if len(self.token_buffer) % 10 == 0:
            new_text = ''.join(self.token_buffer)
            asyncio.create_task( self.context.bot.edit_message_text(chat_id=self.chat_id, message_id=self.message_id, text=new_text))


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Heya! Just chat with me.")


async def handle_message(update: Update, context: CallbackContext):
    msg = await update.message.reply_text("Processing...")
    # Initialize GPT4All model
    llm = GPT4All(model=LLM_PATH,max_tokens=512)
    prompt = PromptTemplate(input_variables=["input_text"], template="{input_text}")
    chain = prompt | llm# | memory

    # Create a callback handler for editing the message
    callback_handler = TelegramEditCallbackHandler(
        context=context,
        chat_id=update.effective_chat.id,
        message_id=msg.message_id
    )

    # Run the chain with the callback handler
    chain.invoke(update.message.text, [callback_handler])
