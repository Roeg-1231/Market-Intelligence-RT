import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.storage.database import init_db
from src.processing.processor import DataProcessor

def run():
    print("=== INICIANDO PIPELINE DE NLP Y ALMACENAMIENTO ===")
    
    try:
        init_db()
    except Exception as e:
        print("Abortando proceso, verifique su Base de Datos local.")
        sys.exit(1)
        
    processor = DataProcessor()
    processor.run_batch()
    
    # === FASE 5: VALIDACIÓN DE MERCADO ===
    from src.ingestion.collector_finance import fetch_historical_prices
    from src.processing.validator import correlate_and_validate
    from src.storage.models_db import StockPrice
    
    symbol = "QQQ" # Nasdaq 100
    prices_raw = fetch_historical_prices(symbol=symbol, days=7)
    try:
        db = processor.db
        for pr in prices_raw:
             rec = StockPrice(symbol=pr["symbol"], fecha=pr["fecha"], open_price=pr["open_price"], close_price=pr["close_price"], volume=pr["volume"])
             db.add(rec)
        db.commit()
        
        # Cruzar fechas para determinar "market_validated" (T+4h)
        correlate_and_validate(db, default_symbol=symbol)
    except Exception as e:
        print("Fallo en módulo de Backtesting Financiero:", e)

    print("\n=== CLASIFICACIÓN FINALIZADA ===")

if __name__ == "__main__":
    run()
