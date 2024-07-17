import os
os.system("curl -fsSL https://ollama.com/install.sh | sh")
os.system("ollama pull llama3")

import streamlit as st
from langchain_core.messages import ChatMessage
from langchain_community.chat_models import ChatOllama
from lib.utils import translate_text, extract_transcript, print_messages, stream_parser_default
from prompt import basic_prompt, chat_history_prompt
language_dict = {"Korean": "ko", "English": "en"}

# Initialize session state to track layout
st.set_page_config(page_title="Youtube paper", page_icon="😊")

if "llm" not in st.session_state:
    st.session_state["llm"] = ChatOllama(model="llama3", temperature=0)
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Sidebar
st.sidebar.title("Language Selection")
video_id = st.sidebar.text_input("YouTube Video ID:")
language = st.sidebar.radio("Choose a language", ("Korean", "English"))
submit_button = st.sidebar.button("Go!")

# Chat
st.title("YouTube Video Summarizer :tv:")
if "transcript" not in st.session_state:
    st.write("Enter a YouTube video ID to get a summary of its content.")

print_messages()

if "video_id" in st.session_state:
    VIDEO_URL = f"https://www.youtube.com/embed/{video_id}"
    st.sidebar.video(VIDEO_URL)

# Sidebar button
if submit_button and video_id:
    try:
        with st.spinner():
            VIDEO_URL = f"https://www.youtube.com/embed/{video_id}"
            st.sidebar.video(VIDEO_URL)
            transcript = extract_transcript(video_id)
            st.session_state["transcript"] = transcript
            llm = st.session_state["llm"]
            chat_chain = basic_prompt | llm
            output = chat_chain.invoke({"input": transcript})
            summary = output.content
            summary_transl = translate_text(summary, language_dict[language])
            with st.chat_message("assistant"):
                st.write(summary_transl)
        
        st.session_state["messages"] = []
        st.session_state["chat_history"] = []

        st.session_state["messages"].append(ChatMessage(role="assistant", content=summary_transl))
        st.session_state["chat_history"].append(("human", "Can you summarize this?\n"+transcript))
        st.session_state["chat_history"].append(("ai", summary))
        st.session_state["video_id"] = video_id
        st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred: {e}")

if "transcript" in st.session_state:
    user_input = st.chat_input("How can I help you?")
    if user_input:
    # if "transcript" not in st.session_state:
    #     st.error("Not available. Please enter a YouTube video ID and press the 'Go!' button.")
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state["messages"].append(ChatMessage(role="user", content=user_input))

        llm = st.session_state["llm"]

        chat_chain = chat_history_prompt | llm

        output = chat_chain.invoke({"input": user_input, "chat_history": st.session_state["chat_history"]})
        answer = output.content
        answer_transl = translate_text(answer, language_dict[language])
        with st.chat_message("assistant"):
            st.write(answer_transl)

        st.session_state["messages"].append(ChatMessage(role="assistant", content=answer_transl))
        st.session_state["chat_history"].append(("human", user_input))
        st.session_state["chat_history"].append(("ai", answer))