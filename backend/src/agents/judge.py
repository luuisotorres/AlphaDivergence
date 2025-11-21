import json
from src.services.llm import LLMService
from src.utils.logger import get_logger

logger = get_logger(__name__)

class JudgeAgent:
    def __init__(self, openai_key: str = None, gemini_key: str = None):
        self.name = "The Judge"
        self.llm = LLMService(openai_key=openai_key, gemini_key=gemini_key)

    def assess_risk(self, hype_data: dict, onchain_data: dict):
        """
        Uses LLM to compare hype vs reality and issue a verdict.
        """
        logger.info(f"[{self.name}] Assessing risk using AI...")
        
        # Construct Prompt
        prompt = f"""
        You are "The Judge", an expert crypto analyst detecting "Fake Hype" and "Rug Pulls".
        Analyze the following data for token: {hype_data.get('token', 'Unknown')}

        ### Agent A (Social Hype) Data:
        {json.dumps(hype_data, indent=2)}

        ### Agent B (On-Chain/Market) Data:
        {json.dumps(onchain_data, indent=2)}

        ### Task:
        Compare the social sentiment (Hype) against the actual on-chain metrics (Reality).
        - If Hype is High but Liquidity/Volume is Low or Selling is High -> High Risk (Fake Hype).
        - If Hype is High and Buying is High -> Potential Gem.
        - If Hype is Low but Buying is High -> Accumulation (Hidden Gem).

        ### Output Format:
        Return ONLY a JSON object with these keys:
        - risk_level (Low, Medium, High, Critical)
        - verdict (Short phrase, e.g., "Rug Pull Risk", "Organic Growth")
        - reasoning (A concise explanation of why, max 2 sentences)
        """

        response_text = self.llm.generate_text(prompt)
        
        # Parse JSON response
        try:
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            verdict_data = json.loads(cleaned_text)
        except Exception as e:
            logger.error(f"[{self.name}] Error parsing LLM response: {e}")
            # Fallback
            verdict_data = {
                "risk_level": "Unknown",
                "verdict": "AI Error",
                "reasoning": "Failed to generate AI verdict."
            }

        return {
            "risk_level": verdict_data.get("risk_level", "Unknown"),
            "verdict": verdict_data.get("verdict", "Unknown"),
            "reasoning": verdict_data.get("reasoning", ""),
            "input_summary": {
                "hype_score": hype_data.get("hype_score"),
                "smart_money_flow": onchain_data.get("net_smart_money_flow")
            }
        }
