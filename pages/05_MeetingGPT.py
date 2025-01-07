import streamlit as st
import subprocess
from pydub import AudioSegment
import math
import openai
import glob
import os

has_transcript = os.path.exists(
    "./.cache/Ryan Holiday ON_ How To AVOID BEING MISERABLE For The Rest of"
    " Your Life _ Jay Shetty.txt"
)


@st.cache_data()
def trancript_chunks(chunk_folder, destination):
    if has_transcript:
        return
    files = glob.glob(f"{chunk_folder}/*.mp3")
    files.sort()
    final_transcript = ""
    for file in files:
        with open(file, "rb") as audio_file, open(
            destination, "a"
        ) as text_file:
            trancript = openai.Audio.transcribe(
                "whisper-1",
                audio_file,
            )
            text_file.write(trancript["text"])


@st.cache_data()
def extact_audio_from_video(video_path):
    if has_transcript:
        return
    audio_path = video_path.replace("mp4", "mp3")
    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        audio_path,
    ]
    subprocess.run(command)


@st.cache_data()
def cut_audio_in_chunks(audio_path, chunk_size, chunks_folder):
    if has_transcript:
        return
    track = AudioSegment.from_mp3(audio_path)
    chunk_len = chunk_size * 60 * 1000
    chunks = math.ceil(len(track) / chunk_len)
    for i in range(chunks):
        start_time = i * chunk_len
        end_time = (i + 1) * chunk_len
        chunk = track[start_time:end_time]
        chunk.export(f"{chunks_folder}/chunk_{i}.mp3", format="mp3")


st.set_page_config(
    page_title="MeetingGPT",
    page_icon="💼",
)

st.header("This is Audio GPT", divider="violet")

st.markdown(
    """
# MeetingGPT
            
Welcome to MeetingGPT, upload a video and I will give you a transcript, a summary and a chat bot to ask any questions about it.
Get started by uploading a video file in the sidebar.
"""
)
with st.sidebar:
    video = st.file_uploader(
        "Video",
        type=["avi", "mp4", "mkv", "mov"],
    )


if video:
    chunks_folder = "./.cache/chunks"
    with st.status("Loading video..."):
        video_content = video.read()
        video_path = f"./.cache/{video.name}"
        audio_path = video_path.replace("mp4", "mp3")
        trancript_path = video_path.replace("mp4", "txt")
        with open(video_path, "wb") as f:
            f.write(video_content)
    with st.status("Extracting audio..."):
        extact_audio_from_video(video_path)
    with st.status("Cutting audio segments..."):
        cut_audio_in_chunks(audio_path, 10, chunks_folder)
    with st.status("Transcribing audio..."):
        trancript_chunks(chunks_folder, trancript_path)
