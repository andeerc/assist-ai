from langchain_openai import ChatOpenAI
from .settings import OPENAI_API_KEY


def get_gpt35():
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=OPENAI_API_KEY,
    )

def get_gpt40():
    return ChatOpenAI(
      model="gpt-4o",
      temperature=0,
      api_key=OPENAI_API_KEY,
  )