import os
import requests
from typing import List
from datetime import datetime
import uuid
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from .base_collector import BaseCollector
from .models import MarketDocument

load_dotenv()

class RateLimitException(Exception):
    pass

class NewsAPICollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="newsapi")
        self.api_key = os.getenv("NEWSAPI_KEY")
        self.base_url = "https://newsapi.org/v2/everything"
        
        if not self.api_key or self.api_key == "your_newsapi_key_here":
            raise ValueError("NEWSAPI_KEY no está configurada correctamente en el archivo .env")

    # Reintenta si hay RateLimitException, esperando 2^x * 1 segundos y deteniéndose tras 3 intentos.
    @retry(
        retry=retry_if_exception_type(RateLimitException),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    def fetch_data(self, query: str = "(Earnings OR FED OR Crash OR Breakthrough OR S&P 500)", limit: int = 100) -> List[MarketDocument]:
        print(f"[{self.source_name}] Obteniendo noticias de NewsAPI enfocadas en alto impacto: '{query}'...")
        params = {
            "q": query,
            "apiKey": self.api_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": min(limit, 100)  # La API limitea a 100 por request gratis
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 429:
            print(f"[{self.source_name}] Rate Limit alcanzado. Lanzando excepción para reintento...")
            raise RateLimitException("Demasiados requests a NewsAPI.")
            
        response.raise_for_status() # Lanza HTTPError para códigos 401, 500, etc.
        
        data = response.json()
        articles = data.get("articles", [])
        
        documents = []
        for article in articles:
            # Content or description as fallback
            content = article.get("content") or article.get("description") or ""
            
            # Parsear fecha
            pub_at = article.get("publishedAt")
            try:
                # 2026-04-16T12:00:00Z format -> compatible with fromisoformat in newer datetime
                fecha = datetime.fromisoformat(pub_at.replace("Z", "+00:00"))
            except Exception:
                fecha = datetime.now()
                
            doc = MarketDocument(
                id=str(uuid.uuid4()),
                fecha=fecha,
                titulo=article.get("title", ""),
                fuente=article.get("source", {}).get("name", "Unknown NewsAPI Source"),
                texto_original=content,
                url=article.get("url"),
                autor=article.get("author")
            )
            documents.append(doc)
            
        print(f"[{self.source_name}] Se obtuvieron {len(documents)} artículos.")
        return documents
