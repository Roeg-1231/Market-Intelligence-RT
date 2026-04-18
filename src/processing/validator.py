import datetime
import re
from sqlalchemy.orm import Session
from src.storage.models_db import ProcessedNews, StockPrice
from src.ingestion.collector_finance import fetch_historical_prices

# Lista de Tickers tecnológicos comunes para búsqueda rápida
TECH_TICKERS = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "AMD", "INTC"]

def extract_ticker(text: str):
    """Extrae un ticker de la lista común si se menciona en el texto."""
    for t in TECH_TICKERS:
        if re.search(rf"\b{t}\b", text, re.IGNORECASE):
            return t
    return None

def correlate_and_validate(db: Session, default_symbol: str = "QQQ"):
    print(f"\n--- Iniciando Validación Pro (Ventana 4h) contra {default_symbol} ---")
    
    news = db.query(ProcessedNews).filter(ProcessedNews.market_validated == None).all()
    if not news:
         print("Validación: No hay noticias nuevas.")
         return
         
    # Diccionario para cachear precios y no repetir llamadas a yfinance / DB
    ticker_caches = {}

    validated_count = 0
    total_evaluated = 0
    
    for article in news:
        if article.sentimiento == "neutral":
            article.market_validated = False
            continue
            
        # Determinar qué ticker usar
        ticker_to_use = extract_ticker(article.titulo) or default_symbol
        
        # Cargar precios para este ticker si no están en cache
        if ticker_to_use not in ticker_caches:
            prices = db.query(StockPrice).filter(StockPrice.symbol == ticker_to_use).order_by(StockPrice.fecha).all()
            if not prices and ticker_to_use != default_symbol:
                # Si es un ticker específico y no está en DB, intentar bajarlo al vuelo (7 días)
                raw_data = fetch_historical_prices(ticker_to_use, days=7)
                for r in raw_data:
                    db.add(StockPrice(**r))
                db.commit()
                prices = db.query(StockPrice).filter(StockPrice.symbol == ticker_to_use).order_by(StockPrice.fecha).all()
            
            ticker_caches[ticker_to_use] = {p.fecha.replace(tzinfo=None): p for p in prices}

        cache = ticker_caches[ticker_to_use]
        if not cache:
            continue

        # Lógica de ventana horaria
        news_time = article.fecha.replace(minute=0, second=0, microsecond=0)
        target_time = news_time + datetime.timedelta(hours=4)
        
        # Buscar precio inicial (P0)
        p0_rec = cache.get(news_time)
        # Buscar precio 4h después (P4)
        p4_rec = cache.get(target_time)

        # Si no hay match exacto, buscar el más cercano en un rango de 1 hora
        if not p0_rec:
            for offset in [-1, 1]:
                p0_rec = cache.get(news_time + datetime.timedelta(hours=offset))
                if p0_rec: break
        
        if not p4_rec:
             for offset in [-1, 1, 2]:
                p4_rec = cache.get(target_time + datetime.timedelta(hours=offset))
                if p4_rec: break

        if p0_rec and p4_rec:
            article.market_validated = False
            market_move_up = p4_rec.close_price > p0_rec.open_price
            
            if article.sentimiento == "positive" and market_move_up:
                article.market_validated = True
            elif article.sentimiento == "negative" and not market_move_up:
                article.market_validated = True
            
            # Solo contamos para la estadística global si supera el umbral de confianza 0.90
            if article.confianza > 0.90:
                total_evaluated += 1
                if article.market_validated:
                    validated_count += 1
                    
    try:
        db.commit()
        if total_evaluated > 0:
            acc = (validated_count / total_evaluated) * 100
            print(f"Validación Completada (Confidence > 0.90). Precisión: {acc:.1f}%")
        else:
            print("No se encontraron suficientes noticias de ALTA CONFIANZA con datos bursátiles para validar.")
    except Exception as e:
        db.rollback()
        print(f"Error registrando validación: {e}")
