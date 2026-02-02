from openai import OpenAI
import streamlit as st

class OpenAIClient:

  def __init__(self) -> None:
    self.api_key = st.secrets["open_ai"]["api_key"]
    self.client = OpenAI(api_key=self.api_key)
    self.model = "gpt-4o-transcribe"

  def transcribe_audio(self, audio_path: str) -> str:
      with open(audio_path, "rb") as audio_file:
          transcript = self.client.audio.transcriptions.create(
              model=self.model,
              file=audio_file,
          )
      return transcript.text