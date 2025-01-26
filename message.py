from asyncio import run
import asyncio

from langchain.chains.conversation.base import ConversationChain
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms.gpt4all import GPT4All
from langchain_core.outputs import LLMResult
from langchain_core.prompts import PromptTemplate
from telegram import Update, Bot
from telegram.ext import CallbackContext


from config import LLM_PATH, ADMINS
from langchain_core.callbacks import BaseCallbackHandler


#memory = ConversationBufferMemory()


class TelegramEditCallbackHandler(BaseCallbackHandler):
    def __init__(self, context, chat_id, message_id):
        self.context = context
        self.chat_id = chat_id
        self.message_id = message_id
        self.token_buffer = []

    def on_llm_end(self, result: LLMResult, **kwargs) -> None:
        print(result)
        asyncio.create_task( self.context.bot.edit_message_text(chat_id=self.chat_id, message_id=self.message_id, text=result.generations[0][0].text))


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Heya! Just chat with me.")


async def handle_message(update: Update, context: CallbackContext):
    msg = await update.message.reply_text("Processing...")
    # Initialize GPT4All model
    callback_handler = TelegramEditCallbackHandler(
        context=context,
        chat_id=update.effective_chat.id,
        message_id=msg.message_id
    )
    llm = GPT4All(model=LLM_PATH,max_tokens=256,)
    prompt = PromptTemplate(input_variables=["input_text"], template="You are a helpful assistant for the user. The user is a syrian girl named Ghazal. The user studies linguistics at university. Only provide a single response. Don'T spin the dialog further. Only return your response after <|assistant|>.\nUser: {input_text}")
    chain = prompt | llm

    response = chain.invoke({"input_text": update.message.text})
    print(response)
    await msg.edit_text(response)
