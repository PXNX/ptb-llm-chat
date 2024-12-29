from asyncio import run
import asyncio
from langchain_community.llms.gpt4all import GPT4All
from langchain_core.prompts import PromptTemplate
from telegram import Update, Bot
from telegram.ext import CallbackContext


from config import LLM_PATH, ADMINS
from langchain_core.callbacks import BaseCallbackHandler

count = 0


class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, update:Update, ):
        super().__init__()
        self.update = update

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        global count
        if count < 10:
            print(f"Token: {token}")
            count += 1
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.update.message.reply_text(text=f"Token: {token}" ))




prompt = PromptTemplate(
    input_variables=["question"],#['instruction', 'input', 'response'],
    template="""
    ### question:
    {question}  """ )

chain = None

def create_llm(bot):
    global chain
    llm = GPT4All(model=LLM_PATH, callbacks=[MyCustomHandler(bot)], streaming=True)
    chain = prompt | llm




llm2 = GPT4All(model=LLM_PATH)



async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Heya! Just chat with me.")


async def handle_message(update: Update, context: CallbackContext):
    await update.message.reply_text("Processing...")
    create_llm(update)
    response  = chain.invoke({"question": update.message.text})
    await update.message.reply_text("Processing... 2")
    response = llm2.invoke([update.message.text])

    await update.message.reply_text(response)
