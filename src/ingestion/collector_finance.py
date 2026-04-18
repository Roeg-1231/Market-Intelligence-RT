import yfinance as yf
from datetime import datetime, timedelta
import warnings

def fetch_historical_prices(symbol: str = "QQQ", days: int = 7):
    """
    Descarga precios OHLC históricos con resolución horaria (intradía). 
    QQQ equivale a Nasdaq 100.
    """
    print(f"[FinanceAPI] Ingiriendo precios INTRADÍA (1h) de {symbol} de los últimos {days} días...")
    
    try:
        ticker = yf.Ticker(symbol)
        # Periodo ajustado a días, intervalo 1h para ventana T+4h
        df = ticker.history(period=f"{days}d", interval="1h")
        
        if df.empty:
            warnings.warn(f"No se encontraron precios para {symbol} en la API.")
            return []
            
        records = []
        for index, row in df.iterrows():
            records.append({
                "symbol": symbol,
                "fecha": index.to_pydatetime(),
                "open_price": float(row['Open']),
                "close_price": float(row['Close']),
                "volume": float(row['Volume'])
            })
        print(f"[FinanceAPI] Extracción exitosa: {len(records)} velas horarias de {symbol}.")
        return records
    except Exception as e:
        warnings.warn(f"[FinanceAPI] yFinance falló, asegurate de tener conexión: {e}")
        return []
