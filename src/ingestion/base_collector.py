from abc import ABC, abstractmethod
from typing import List
from .models import MarketDocument
import os
from datetime import datetime

class BaseCollector(ABC):
    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def fetch_data(self, query: str, limit: int = 100) -> List[MarketDocument]:
        """Extrae los datos desde la fuente y los devuelve en formato estandarizado."""
        pass

    def save_to_raw(self, documents: List[MarketDocument], base_dir: str = "data/raw"):
        """Guarda la lista de documentos en el directorio data/raw como JSON Lines."""
        if not documents:
            print(f"[{self.source_name}] No hay documentos para guardar.")
            return

        date_str = datetime.now().strftime("%Y-%m-%d")
        folder_path = os.path.join(base_dir, self.source_name, date_str)
        os.makedirs(folder_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%H%M%S")
        file_path = os.path.join(folder_path, f"data_{timestamp}.jsonl")
        
        with open(file_path, "w", encoding="utf-8") as f:
            for doc in documents:
                # Serializa el modelo usando Pydantic, convierte fecha con datetime seguro
                f.write(doc.model_dump_json() + "\n")
                
        print(f"[{self.source_name}] Guardados {len(documents)} documentos en {file_path}")
