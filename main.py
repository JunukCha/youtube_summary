import streamlit as st
from langchain_core.messages import ChatMessage
from langchain_community.chat_models import ChatOpenAI
from lib.utils import translate_text, extract_transcript, print_messages, stream_parser_default, init_session
from prompt import basic_prompt, chat_history_prompt
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# nltk.download('punkt')

language_dict = {"korean": "ko", "english": "en"}

# Initialize session state to track layout
st.set_page_config(page_title="Youtube Summary", page_icon="😊")


if 'run_go_button' in st.session_state \
    and st.session_state.run_go_button == True:
    st.session_state.running = True
else:
    st.session_state.running = False

model = st.sidebar.selectbox("Model", ["Basic", "gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"], disabled=st.session_state.running, on_change=init_session)

if "gpt" in model:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", disabled=st.session_state.running, type="password")
    target_n_sentences = None
else:
    openai_api_key = None
    target_n_sentences = st.sidebar.text_input("The number of sentences", disabled=st.session_state.running)

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Sidebar
st.sidebar.title("Language Selection")
video_id = st.sidebar.text_input("YouTube Video ID:")
language = st.sidebar.radio("Choose a language", ("korean", "english"))
submit_button = st.sidebar.button("Go!", key='run_go_button')

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
    if "llm" not in st.session_state and "gpt" in model:
        st.session_state["llm"] = ChatOpenAI(openai_api_key=openai_api_key, model_name=model)
    elif "llm" not in st.session_state and model == "Basic":
        st.session_state["llm"] = LsaSummarizer()

    try:
        with st.spinner():
            transcript = extract_transcript(video_id)
            st.session_state["transcript"] = transcript
            llm = st.session_state["llm"]

            if "gpt" in model:
                chat_chain = basic_prompt | llm
                output = chat_chain.invoke({"input": transcript, "language": language})
                summary = output.content
            else:
                parser = PlaintextParser.from_string(transcript, Tokenizer("korean"))
                output = llm(parser.document, target_n_sentences)  # 요약 문장 수 설정
                summary = ""
                for sentence in output:
                    summary += str(sentence)+"\n"

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

if "transcript" in st.session_state and "gpt" in model:
    user_input = st.chat_input("How can I help you?")
    if user_input:
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