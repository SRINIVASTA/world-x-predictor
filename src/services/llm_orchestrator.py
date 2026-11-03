from groq import Groq
import streamlit as st
from config.logger_config import setup_logger

logger = setup_logger("llm_orchestrator")

def summarize_news_with_groq(headlines: list) -> str:
    if not headlines:
        return "No headlines provided to summarize."

    try:
        # Access secret variable token from Streamlit securely
        api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
        
        prompt = "Summarize the following recent news headlines for investors:\n\n" + "\n".join([f"- {h}" for h in headlines])
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a financial analyst helper. Provide clear, objective, bulleted investor summaries based solely on the provided headlines."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=512
        )
        return completion.choices.message.content.strip()
    except Exception as e:
        logger.error(f"Groq API transaction anomaly detected: {str(e)}")
        raise RuntimeError(f"AI Synthesis pipeline failed: {str(e)}")
