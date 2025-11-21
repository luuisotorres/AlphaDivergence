from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from src.agents.listener import ListenerAgent
from src.agents.analyst import AnalystAgent
from src.agents.judge import JudgeAgent
from src.utils.security import sanitize_error_message
from src.utils.logger import get_logger
from typing import Optional
import os

logger = get_logger(__name__)

app = FastAPI(
    title="AlphaDivergence API",
    root_path=os.getenv("ROOT_PATH", "")  # Support for running behind proxy
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AlphaDivergence Backend is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {
        "status": "healthy",
        "service": "alphadivergence-backend",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/analyze/{token}")
def analyze_token(
    token: str,
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key"),
    x_gemini_key: Optional[str] = Header(None, alias="X-Gemini-Key"),
    x_etherscan_key: Optional[str] = Header(None, alias="X-Etherscan-Key"),
    x_reddit_client_id: Optional[str] = Header(None, alias="X-Reddit-Client-Id"),
    x_reddit_client_secret: Optional[str] = Header(None, alias="X-Reddit-Client-Secret"),
    x_reddit_user_agent: Optional[str] = Header(None, alias="X-Reddit-User-Agent")
):
    """
    Orchestrates the agents to analyze a token.
    Accepts API keys via headers (X-OpenAI-Key, X-Gemini-Key, etc.) or falls back to environment variables.
    """
    # Collect sensitive values for potential sanitization (filter out None values)
    sensitive_values = [
        v for v in [x_openai_key, x_gemini_key, x_etherscan_key,
                    x_reddit_client_id, x_reddit_client_secret]
        if v is not None
    ]
    
    # Initialize Agents with optional API keys from headers
    # Wrap in try-catch to prevent API key leakage in error messages
    try:
        listener = ListenerAgent(
            reddit_client_id=x_reddit_client_id,
            reddit_client_secret=x_reddit_client_secret,
            reddit_user_agent=x_reddit_user_agent,
            openai_key=x_openai_key,
            gemini_key=x_gemini_key
        )
    except Exception as e:
        sanitized_error = sanitize_error_message(e, sensitive_values)
        logger.error(f"Failed to initialize ListenerAgent: {sanitized_error}")
        raise HTTPException(status_code=500, detail="Failed to initialize Listener agent")
    
    try:
        analyst = AnalystAgent(etherscan_api_key=x_etherscan_key)
    except Exception as e:
        sanitized_error = sanitize_error_message(e, sensitive_values)
        logger.error(f"Failed to initialize AnalystAgent: {sanitized_error}")
        raise HTTPException(status_code=500, detail="Failed to initialize Analyst agent")
    
    try:
        judge = JudgeAgent(openai_key=x_openai_key, gemini_key=x_gemini_key)
    except Exception as e:
        sanitized_error = sanitize_error_message(e, sensitive_values)
        logger.error(f"Failed to initialize JudgeAgent: {sanitized_error}")
        raise HTTPException(status_code=500, detail="Failed to initialize Judge agent")
    
    # 1. Listener Agent
    hype_data = listener.analyze_sentiment(token)
    
    # 2. Analyst Agent
    onchain_data = analyst.analyze_onchain_data(token)
    
    # 3. Judge Agent
    verdict = judge.assess_risk(hype_data, onchain_data)
    
    return {
        "token": token,
        "hype_analysis": hype_data,
        "onchain_analysis": onchain_data,
        "final_verdict": verdict
    }
