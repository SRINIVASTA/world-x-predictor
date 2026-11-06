from groq import Groq
import streamlit as st
import json
from config.logger_config import setup_logger

logger = setup_logger("llm_orchestrator")

def analyze_and_summarize_news(ticker: str, asset_class: str, headlines: list) -> dict:
    """
    Unified multi-task function that extracts a narrative investor summary
    and a structured quantitative sentiment rating matrix in a single LLM loop.
    """
    if not headlines:
        return {
            "summary": "No headlines provided to summarize.",
            "composite_score": 0.0,
            "label": "Neutral",
            "breakdown": []
        }

    try:
        # Secure token retrieval from Streamlit platform configurations
        api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
        
        formatted_headlines = "\n".join([f"- {h}" for h in headlines])

        system_prompt = (
            "You are an enterprise-grade financial quant analyst and assistant system.\n"
            "Analyze the provided headlines to build an investor summary and calculate a sentiment matrix.\n"
            "You must return ONLY a valid, minified JSON object matching this schema exactly:\n"
            "{\n"
            '  "summary": "string (clear, bulleted investor summary highlighting performance, risks, and trends)",\n'
            '  "composite_score": float (between -1.00 and 1.00 representing total net asset momentum),\n'
            '  "label": string ("Strongly Bearish", "Bearish", "Neutral", "Bullish", "Strongly Bullish"),\n'
            '  "breakdown": [\n'
            "    {\n"
            '      "headline": string,\n'
            '      "score": float (between -1.00 and 1.00),\n'
            '      "impact_weight": float (0.0 to 1.0)\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "Do not include markdown blocks like ```json or any trailing conversational text."
        )

        user_prompt = f"Asset Ticker: {ticker}\nAsset Class: {asset_class}\nHeadlines:\n{formatted_headlines}"

        completion = client.chat.completions.create(
            model="llama3-3b-8b-instant",  # Highly responsive model for reliable JSON structured frameworks
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Kept minimal to enforce strict analytical parameters
            response_format={"type": "json_object"}
        )
        
        if completion.choices and len(completion.choices) > 0:
            raw_output = completion.choices[0].message.content.strip()
            return json.loads(raw_output)
        else:
            logger.error("Groq engine processing framework yielded an empty choice matrix.")
            raise ValueError("Empty choice matrix returned from model.")
            
    except Exception as e:
        logger.error(f"Groq API transaction anomaly detected: {str(e)}")
        # Production structural fallback layout to protect your user interface execution flow
        return {
            "summary": f"⚠️ News compilation paused due to pipeline variance: {str(e)}",
            "composite_score": 0.00,
            "label": "Neutral (Execution Fallback)",
            "breakdown": [{"headline": h, "score": 0.0, "impact_weight": 0.33} for h in headlines]
        }
