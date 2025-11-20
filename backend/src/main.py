from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from src.agents.listener import ListenerAgent
from src.agents.analyst import AnalystAgent
from src.agents.judge import JudgeAgent
import os

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

# Initialize Agents
listener = ListenerAgent()
analyst = AnalystAgent()
judge = JudgeAgent()

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
def analyze_token(token: str):
    """
    Orchestrates the agents to analyze a token.
    """
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
