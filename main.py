import streamlit as st
from langchain_core.messages import ChatMessage
from langchain_community.chat_models import ChatOpenAI
from lib.utils import (
    translate_text, extract_transcript, 
    print_messages, save_chat_to_docx, 
    update_token_usage, show_cost, 
    extract_video_id
)
from lib.prompt import basic_prompt, chat_history_prompt
from lib.constants import language_dict

# Initialize session state to track layout
st.set_page_config(page_title="Youtube Summary", page_icon="😊")

if 'run_go_button' in st.session_state \
    and st.session_state.run_go_button == True:
    st.session_state.running = True
else:
    st.session_state.running = False

if "llm" not in st.session_state:
    st.sidebar.title("Model Selection")
    model = st.sidebar.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"], disabled=st.session_state.running)
    openai_api_key = st.sidebar.text_input("OpenAI API Key", disabled=st.session_state.running, type="password")
    st.sidebar.markdown("[OPENAI API Key](https://platform.openai.com/api-keys)")
    st.session_state["model"] = model

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "total_tokens" not in st.session_state:
    st.session_state["total_tokens"] = 0
if "prompt_tokens" not in st.session_state:
    st.session_state["prompt_tokens"] = 0
if "completion_tokens" not in st.session_state:
    st.session_state["completion_tokens"] = 0

if "video_id" not in st.session_state:
    # Sidebar
    st.sidebar.title("Language Selection")
    video_id = st.sidebar.text_input("YouTube URL or Video ID:", disabled=st.session_state.running)
    video_id = extract_video_id(video_id)
    language = st.sidebar.radio("Choose a language", ("korean", "english"))
    submit_button = st.sidebar.button("Go!", key='run_go_button')
    st.session_state["language"] = language
else:
    video_id = st.session_state["video_id"]
    VIDEO_URL = f"https://www.youtube.com/embed/{video_id}"
    st.sidebar.video(VIDEO_URL)
    submit_button = None

# Chat
st.title("YouTube Video Summarizer :tv:")
if "transcript" not in st.session_state:
    st.write("Enter a YouTube video ID to get a summary of its content.")

print_messages()

# Sidebar button
if submit_button and video_id:
    if "llm" not in st.session_state:
        st.session_state["llm"] = ChatOpenAI(openai_api_key=openai_api_key, model_name=model)

    try:
        with st.spinner():
            transcript = extract_transcript(video_id)
            st.session_state["transcript"] = transcript

            llm = st.session_state["llm"]
            chat_chain = basic_prompt | llm
            language = st.session_state["language"]
            output = chat_chain.invoke({"input": transcript, "language": language})
            update_token_usage(output.response_metadata['token_usage'])

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
        with st.spinner():
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state["messages"].append(ChatMessage(role="user", content=user_input))

            llm = st.session_state["llm"]

            chat_chain = chat_history_prompt | llm

            output = chat_chain.invoke({"input": user_input, "chat_history": st.session_state["chat_history"]})
            print(output.response_metadata['token_usage'])
            update_token_usage(output.response_metadata['token_usage'])
                    
            answer = output.content
            language = st.session_state["language"]
            answer_transl = translate_text(answer, language_dict[language])

            with st.chat_message("assistant"):
                st.write(answer_transl)

            st.session_state["messages"].append(ChatMessage(role="assistant", content=answer_transl))
            st.session_state["chat_history"].append(("human", user_input))
            st.session_state["chat_history"].append(("ai", answer))

    doc_buffer = save_chat_to_docx(st.session_state.chat_history)
    st.download_button(
        label="Download DOCX",
        data=doc_buffer,
        file_name="chat_history.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

show_cost(st.session_state.model)