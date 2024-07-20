from langchain.prompts import PromptTemplate

basic_prompt_template="""
SYSTEM

You are the best summarizer.

HUMAN

Summarize the core content of this video. And I think it would be nice if you could tell me in a list format.
Answer in {language}
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