import pandas as pd
from sqlalchemy import text
from src.storage.database import engine

def fetch_all_processed_news() -> pd.DataFrame:
    query = """
    SELECT titulo, fecha, fuente, texto_procesado, sentimiento, confianza, market_validated, razonamiento 
    FROM processed_news 
    ORDER BY fecha DESC
    """
    df = pd.read_sql_query(query, engine)
    return df

def fetch_sentiment_summary() -> pd.DataFrame:
    query = """
    SELECT sentimiento, COUNT(*) as cantidad
    FROM processed_news
    GROUP BY sentimiento
    """
    df = pd.read_sql_query(query, engine)
    return df

def fetch_financial_metrics() -> pd.DataFrame:
    query = """
    SELECT fecha, close_price 
    FROM stock_prices 
    WHERE symbol='^GSPC' 
    ORDER BY fecha ASC
    """
    return pd.read_sql_query(query, engine)

def fetch_accuracy() -> float:
    # Solo consideramos éxito real para noticias con ALTA CONFIANZA (> 0.90)
    query = "SELECT COUNT(*) FROM processed_news WHERE market_validated = TRUE AND confianza > 0.90 AND sentimiento != 'neutral'"
    query_total = "SELECT COUNT(*) FROM processed_news WHERE market_validated IS NOT NULL AND confianza > 0.90 AND sentimiento != 'neutral'"
    with engine.connect() as conn:
        hits = conn.execute(text(query)).scalar() or 0
        total = conn.execute(text(query_total)).scalar() or 0
    return (hits / total * 100) if total > 0 else 0
