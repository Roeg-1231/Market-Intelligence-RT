from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from .database import Base
from datetime import datetime

class ProcessedNews(Base):
    __tablename__ = "processed_news"

    id = Column(Integer, primary_key=True, index=True)
    original_id = Column(String, unique=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    titulo = Column(String)
    fuente = Column(String)
    texto_procesado = Column(String)
    
    sentimiento = Column(String, index=True) 
    confianza = Column(Float)
    razonamiento = Column(String) # Razón extraída por NLP Heurístico
    market_validated = Column(Boolean, nullable=True) # Flag validación de mercado

class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    fecha = Column(DateTime, index=True)
    open_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)
