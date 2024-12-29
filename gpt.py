# Import dependencies
from langchain.chains.llm import LLMChain
from langchain_community.llms.gpt4all import GPT4All
from langchain_core.prompts import PromptTemplate

# Specify model weights path
PATH='C:/Users/nyx/AppData/Local/nomic.ai/GPT4All/qwen2-1_5b-instruct-q4_0.gguf'

# Create LLM Class
llm = GPT4All(model=PATH, verbose=True)

# Create a prompt template
prompt = PromptTemplate(
    input_variables=['instruction', 'input', 'response'],
    template="""
    ### Instruction:
    {instruction}
    ### Input:
    {input}
    ### Response:
    {response}
    """ )

chain = prompt | llm

import time
start = time.process_time()

# Run the prompt
# I used a childen story to test https://cuentosparadormir.com/infantiles/cuento/barba-flamenco-y-el-recortador-de-cuentos
# its about 783 words long!
rs =chain.invoke({"instruction":"""Resume esta historia, hazlo en español""",
"input":"""[...story content...]""",
"response":'A: '})
print(time.process_time() - start)
print(rs)
##res =llm.invoke("THis is a test")
###print(res)

rs2 = llm.generate(["How can I run LLMs efficiently on my laptop?"], max_tokens=1024)
print(time.process_time() - start)
print(rs2)
