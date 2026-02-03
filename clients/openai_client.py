from openai import OpenAI
import streamlit as st

class OpenAIClient:

  def __init__(self) -> None:
    self.api_key = st.secrets["open_ai"]["api_key"]
    self.client = OpenAI(api_key=self.api_key)
    self.transcribe_model = "gpt-4o-mini-transcribe"
    self.model = "gpt-4.1-2025-04-14"

  def chat(self, prompt: str, temperature) -> str:
    response = self.client.chat.completions.create(
      model=self.model,
      messages=[{"role": "user", "content": prompt}],
      temperature=temperature,
    )
    return response.choices[0].message.content

  def transcribe_audio(self, audio_path: str) -> str:
      with open(audio_path, "rb") as audio_file:
          transcript = self.client.audio.transcriptions.create(
              model=self.transcribe_model,
              file=audio_file,
          )
      return transcript.text