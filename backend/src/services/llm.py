import os
import json
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
from src.utils.logger import get_logger
from src.utils.security import sanitize_error_message

load_dotenv()
logger = get_logger(__name__)

class LLMService:
    def __init__(self, openai_key: str = None, gemini_key: str = None):
        self.provider = None
        self.client = None
        self.model = None
        
        # Priority: Passed keys → Environment variables
        openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        gemini_key = gemini_key or os.getenv("GEMINI_API_KEY")

        if openai_key:
            try:
                self.provider = "openai"
                self.client = OpenAI(api_key=openai_key)
                self.model = "gpt-4o"
                logger.info("[LLMService] Using OpenAI (GPT-4o)")
            except Exception as e:
                sanitized_error = sanitize_error_message(e, [openai_key])
                logger.error(f"[LLMService] Failed to initialize OpenAI: {sanitized_error}")
                # Continue to try Gemini as fallback
                openai_key = None
                
        if not openai_key and gemini_key:
            try:
                self.provider = "gemini"
                genai.configure(api_key=gemini_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                logger.info("[LLMService] Using Gemini (Flash)")
            except Exception as e:
                sanitized_error = sanitize_error_message(e, [gemini_key])
                logger.error(f"[LLMService] Failed to initialize Gemini: {sanitized_error}")
                
        if not self.provider:
            logger.warning("[LLMService] No valid API keys found (OpenAI or Gemini). LLM features disabled.")

    def generate_text(self, prompt: str) -> str:
        """
        Generates text using the configured provider.
        """
        if not self.provider:
            return "Error: No LLM API Key configured."

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful crypto analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
            
            elif self.provider == "gemini":
                response = self.model.generate_content(prompt)
                return response.text
                
        except Exception as e:
            sanitized_error = sanitize_error_message(e, [])
            logger.error(f"[LLMService] Error generating text: {sanitized_error}")
            return f"Error generating text: {sanitized_error}"

    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyzes sentiment of a text and returns structured JSON.
        """
        if not self.provider:
            return {"sentiment_score": 0.5, "sentiment_label": "Neutral", "hype_intensity": "Unknown"}

        prompt = f"""
        Analyze the sentiment of this crypto social media post.
        Text: "{text}"
        
        Return ONLY a JSON object with:
        - sentiment_score (float between 0.0 and 1.0, where 0 is negative, 1 is positive)
        - sentiment_label (Positive, Negative, Neutral)
        """

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a sentiment analysis engine. Output JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0
                )
                result_text = response.choices[0].message.content
            
            elif self.provider == "gemini":
                response = self.model.generate_content(prompt)
                result_text = response.text

            # Clean and parse JSON
            cleaned_text = result_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)

        except Exception as e:
            sanitized_error = sanitize_error_message(e, [])
            logger.error(f"[LLMService] Error analyzing sentiment: {sanitized_error}")
            return {
                "sentiment_score": 0.5,
                "sentiment_label": "Neutral",
                "hype_intensity": "Unknown"
            }
