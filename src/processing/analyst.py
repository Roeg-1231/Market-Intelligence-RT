import os
import requests
import pandas as pd
from dotenv import load_dotenv

class MarketAnalyst:
    def __init__(self):
        self.is_configured = False
        # Forzar recarga en cada refresh para evadir cachés de Streamlit
        load_dotenv(override=True)
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            self.is_configured = True

    def generate_executive_summary(self, news_df: pd.DataFrame) -> str:
        if not self.is_configured:
            return "⚠️ **The Analyst LLM inactivo.** Añade tu `GEMINI_API_KEY` gratuita al archivo `.env`."
            
        if news_df.empty:
            return "Insuficientes datos para reporte ejecutivo."

        top_news = news_df.sort_values(by="confianza", ascending=False).head(10)
        news_text = "\n".join([f"- {row['titulo']} (Predicción NLP: {row['sentimiento']})" for _, row in top_news.iterrows()])
        
        prompt = f"""
        Actúa como un Portfolio Manager o Analista Senior. Basado estrictamente en los siguientes titulares clasificados por nuestro modelo cuantitativo, redacta un Resumen Ejecutivo directo de 3 párrafos analizando '¿Qué está pasando realmente en el mercado?' y cómo afectan estos titulares.
        Aplica un tono bursátil, preciso y sofisticado. Formatea usando Markdown si deseas.
        
        Titulares Top Impacto:
        {news_text}
        """
        
        # Consumo mediante REST API Directo y Puro
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"❌ Error API: Respuesta Inesperada de Google (HTTP {response.status_code})"
        except Exception as e:
            return f"❌ Error generando análisis sintético de red: {str(e)}"
