import os
from abc import ABC
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class BaseAgent(ABC):
    """Base class for AI agents that handle various content types including X.com posts"""
    def __init__(self, model: str = "gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)