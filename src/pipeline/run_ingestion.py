import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ingestion.collector_news import NewsAPICollector
from src.ingestion.collector_reddit import RedditCollector

def run_pipeline(query: str = "(Earnings OR FED OR Crash OR Breakthrough OR S&P 500)"):
    print("=== INICIANDO PIPELINE DE INGESTIÓN ===")
    print(f"Búsqueda objetivo: '{query}'\n")
    
    # 1. Instanciar recolectores
    try:
        news_collector = NewsAPICollector()
    except Exception as e:
        print(f"Error inicializando NewsAPI: {e}")
        news_collector = None
        
    try:
        reddit_collector = RedditCollector()
    except Exception as e:
        print(f"Error inicializando Reddit: {e}")
        reddit_collector = None
        
    # 2. Ejecutar y Guardar NewsAPI
    if news_collector:
        try:
            print("--- Ejecutando NewsAPI ---")
            news_docs = news_collector.fetch_data(query=query, limit=20) # 20 noticias como límite de prueba
            news_collector.save_to_raw(news_docs)
        except Exception as e:
            print(f"Fallo durante la recolección de NewsAPI: {e}")

    # 3. Ejecutar y Guardar Reddit
    if reddit_collector:
        try:
            print("\n--- Ejecutando Reddit ---")
            reddit_docs = reddit_collector.fetch_data(query=query, limit=20)
            reddit_collector.save_to_raw(reddit_docs)
        except Exception as e:
            print(f"Fallo abismal durante la recolección de Reddit: {e}")
            
    print("\n=== PIPELINE FINALIZADO ===")

if __name__ == "__main__":
    run_pipeline(query="(Earnings OR FED OR Crash OR Breakthrough OR S&P 500)")
