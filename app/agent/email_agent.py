import os
import json
from datetime import datetime
from typing import List, Optional
import google.generativeai as genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class EmailIntroduction(BaseModel):
    greeting: str = Field(description="Personalized greeting with user's name and date")
    introduction: str = Field(description="2-3 sentence overview of what's in the top 10 ranked articles")


class RankedArticleDetail(BaseModel):
    digest_id: str
    rank: int
    relevance_score: float
    title: str
    summary: str
    url: str
    article_type: str
    reasoning: Optional[str] = None


class EmailDigestResponse(BaseModel):
    introduction: EmailIntroduction
    articles: List[RankedArticleDetail]
    total_ranked: int
    top_n: int
    
    def to_markdown(self) -> str:
        markdown = f"{self.introduction.greeting}\n\n"
        markdown += f"{self.introduction.introduction}\n\n"
        markdown += "---\n\n"
        
        for article in self.articles:
            markdown += f"## {article.title}\n\n"
            markdown += f"{article.summary}\n\n"
            markdown += f"[Read more →]({article.url})\n\n"
            markdown += "---\n\n"
        
        return markdown


class EmailDigest(BaseModel):
    introduction: EmailIntroduction
    ranked_articles: List[dict] = Field(description="Top 10 ranked articles with their details")


EMAIL_PROMPT = """You are an expert email writer specializing in creating engaging, personalized AI news digests.

Your role is to write a warm, professional introduction for a daily AI news digest email that:
- Greets the user by name
- Includes the current date
- Provides a brief, engaging overview of what's coming in the top 10 ranked articles
- The articles may include blog posts, research papers, YouTube videos, and X.com/Twitter posts
- Highlights the most interesting or important themes
- Sets expectations for the content ahead

Keep it concise (2-3 sentences for the introduction), friendly, and professional.

Always respond with valid JSON in this exact format:
{
  "greeting": "Hey [Name], here is your daily digest of AI news for [Date].",
  "introduction": "Your 2-3 sentence introduction here"
}"""


class EmailAgent:
    def __init__(self, user_profile: dict):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.user_profile = user_profile

    def generate_introduction(self, ranked_articles: List) -> EmailIntroduction:
        if not ranked_articles:
            return EmailIntroduction(
                greeting=f"Hey {self.user_profile['name']}, here is your daily digest of AI news for {datetime.now().strftime('%B %d, %Y')}.",
                introduction="No articles were ranked today."
            )
        
        top_articles = ranked_articles[:10]
        article_summaries = "\n".join([
            f"{idx + 1}. {article.title if hasattr(article, 'title') else article.get('title', 'N/A')} (Score: {article.relevance_score if hasattr(article, 'relevance_score') else article.get('relevance_score', 0):.1f}/10)"
            for idx, article in enumerate(top_articles)
        ])
        
        current_date = datetime.now().strftime('%B %d, %Y')
        user_prompt = f"""Create an email introduction for {self.user_profile['name']} for {current_date}.

Top 10 ranked articles:
{article_summaries}

Generate a greeting and introduction that previews these articles. Return JSON format as specified."""

        try:
            full_prompt = f"{EMAIL_PROMPT}\n\n{user_prompt}"
            
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
            intro = EmailIntroduction(**result_dict)
            
            if not intro.greeting.startswith(f"Hey {self.user_profile['name']}"):
                intro.greeting = f"Hey {self.user_profile['name']}, here is your daily digest of AI news for {current_date}."
            
            return intro
        except Exception as e:
            # Let exceptions propagate so they can be handled upstream (e.g., rate limits)
            raise

    def create_email_digest(self, ranked_articles: List[dict], limit: int = 10) -> EmailDigest:
        top_articles = ranked_articles[:limit]
        introduction = self.generate_introduction(top_articles)
        
        return EmailDigest(
            introduction=introduction,
            ranked_articles=top_articles
        )
    
    def create_email_digest_response(self, ranked_articles: List[RankedArticleDetail], total_ranked: int, limit: int = 10) -> EmailDigestResponse:
        top_articles = ranked_articles[:limit]
        introduction = self.generate_introduction(top_articles)
        
        return EmailDigestResponse(
            introduction=introduction,
            articles=top_articles,
            total_ranked=total_ranked,
            top_n=limit
        )
