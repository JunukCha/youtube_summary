from langchain.prompts import PromptTemplate

basic_prompt_template="""
SYSTEM

You are the best summarizer.

HUMAN

Can you summarize this?
{input}
"""
basic_prompt = PromptTemplate.from_template(basic_prompt_template)

chat_history_prompt_template="""
PLACEHOLDER

{chat_history}

HUMAN

{input}
"""
chat_history_prompt = PromptTemplate.from_template(chat_history_prompt_template)