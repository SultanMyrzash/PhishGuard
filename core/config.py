import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SystemConfig:
    # --- API KEYS ---
    GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")
    LOCAL_API_KEY = "lm-studio"
    LOCAL_BASE_URL = "http://localhost:1234/v1"
    
    # --- STRICT MODEL CONFIGURATION (DO NOT CHANGE) ---
    MODELS = {
        "Local LLM": {
            "provider": "LOCAL",
            "model_name": "local-model", 
            "capabilities": ["text"]
        },
        "Cloud: Gemini Flash (Fast)": {
            "provider": "GOOGLE",
            "model_name": "gemini-flash-latest", 
            "capabilities": ["vision", "reasoning"]
        },
        "Cloud: Gemini 3 pro (thinking)": {
            "provider": "GOOGLE",
            "model_name": "gemini-3-pro-preview", 
            "capabilities": ["vision", "deep-reasoning"]
        }
    }
    
    # --- PROMPTS ---
    PROMPT_SINGLE = """
    ROLE: Senior Digital Forensics Examiner.
    TASK: Analyze the provided artifact (Email Headers/Body or Screenshot).
    
    OBJECTIVES:
    1. Header Forensics: Detect spoofing (SPF/DKIM), mismatched Return-Paths, and anomalous IP routing.
    2. Social Engineering: Identify psychological triggers (Urgency, Fear, Authority).
    3. Payload Analysis: flagging suspicious links or attachments.
    
    OUTPUT FORMAT (Markdown):
    ## 🛡️ Forensic Analysis Report
    **Risk Score:** [0-100] | **Classification:** [Phishing/Safe/Spam]
    
    ### 🚩 Critical Findings
    - [Point 1]
    - [Point 2]
    
    ### 🧠 Technical Reasoning
    [Detailed explanation of the verdict]
    """

    PROMPT_COMPARE = """
    ROLE: Model Evaluator.
    TASK: Analyze the artifact for phishing indicators. Be concise but precise.
    Focus on: Technical anomalies and visual discrepancies.
    """