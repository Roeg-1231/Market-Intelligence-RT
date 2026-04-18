from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class MarketDocument(BaseModel):
    id: str
    fecha: datetime
    titulo: str
    fuente: str
    texto_original: str
    url: Optional[str] = None
    autor: Optional[str] = None
