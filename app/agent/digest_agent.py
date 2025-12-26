import os
import json
from typing import Optional
import google.generativeai as genai
from pydantic import BaseModel
from dotenv import load_dotenv
from app.agent.base import BaseAgent

load_dotenv()


class DigestOutput(BaseModel):
    title: str
    summary: str


PROMPT = """You are an expert AI news analyst specializing in summarizing technical articles, research papers, video content, and social media posts (X.com/Twitter) about artificial intelligence.

Your role is to create concise, informative digests that help readers quickly understand the key points and significance of AI-related content.

Guidelines:
- Create a compelling title (5-10 words) that captures the essence of the content
- Write a 2-3 sentence summary that highlights the main points and why they matter
- Focus on actionable insights and implications
- Use clear, accessible language while maintaining technical accuracy
- Avoid marketing fluff - focus on substance
- For social media posts, extract the key information and context

Always respond with valid JSON in this exact format:
{
  "title": "Your title here",
  "summary": "Your summary here"
}"""


class DigestAgent(BaseAgent):
    def __init__(self):
        super().__init__("gemini-2.5-flash")
        self.system_prompt = PROMPT

    def generate_digest(self, title: str, content: str, article_type: str) -> Optional[DigestOutput]:
        try:
            user_prompt = f"Create a digest for this {article_type}: \n Title: {title} \n Content: {content[:8000]}"
            
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.7,
                }
            )
            
            # Parse JSON from response
            response_text = response.text.strip()
            # Extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result_dict = json.loads(response_text)
            return DigestOutput(**result_dict)
        except Exception as e:
            # Let exceptions propagate so they can be handled upstream (e.g., rate limits)
            raise
