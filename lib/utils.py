import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator

def translate_text(text, dest_lang):
    translator = Translator()
    detected = translator.detect(text)
    if detected == dest_lang:
        return text
    translation = translator.translate(text, dest_lang)
    return translation.text

def extract_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
    transcript_text = " ".join([entry['text'] for entry in transcript])
    transcript_text = translate_text(transcript_text, "en")
    return transcript_text

def print_messages():
    if "messages" in st.session_state and len(st.session_state["messages"]) > 0:
        for chat_message in st.session_state["messages"]:
            st.chat_message(chat_message.role).write(chat_message.content)

def stream_parser_default(stream):
    for chunk in stream:
        yield chunk.content