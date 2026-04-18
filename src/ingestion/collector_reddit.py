import os
from typing import List
import warnings
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from .base_collector import BaseCollector
from .models import MarketDocument

class RedditRateLimitException(Exception):
    pass

class RedditCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="reddit")
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        
        # Initialization logic for PRAW would go here.
        if not self.client_id or self.client_id == "your_reddit_client_id":
            warnings.warn("Credenciales de Reddit no encontradas. El módulo se ejecutará en modo simulado/placeholder.")
            self.is_configured = False
        else:
            self.is_configured = True

    @retry(
        retry=retry_if_exception_type(RedditRateLimitException),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3)
    )
    def fetch_data(self, query: str = "S&P 500", limit: int = 100) -> List[MarketDocument]:
        print(f"[{self.source_name}] Inicializando búsqueda en Reddit para: '{query}'...")
        
        if not self.is_configured:
            print(f"[{self.source_name}] ADVERTENCIA: Funcionalidad simulada. No se ejecutarán llamadas a la API.")
            return []
            
        # TODO: Implementar integración real usando PRAW cuando las credenciales estén listas.
        return []
