import os
import json
import shutil
import warnings
from typing import List, Dict, Any
from datetime import datetime
from transformers import pipeline

from src.storage.database import SessionLocal
from src.storage.models_db import ProcessedNews

class NLPProcessor:
    def __init__(self):
        print("Cargando modelo NLP estructurado por FinBERT...")
        # Usa ProsusAI/finbert que clasifica finanzas a perfection
        self.classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert")
        print("Modelo FinBERT AI cargado.")

    def process_text_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        # Truncar textos demasiado largos
        truncated_texts = [str(text)[:1500] if text else " " for text in texts]
        try:
            results = self.classifier(truncated_texts, truncation=True, max_length=512)
            return results
        except Exception as e:
            warnings.warn(f"Error procesando lote en Transformers NLP: {e}")
            return [{"label": "neutral", "score": 0.0} for _ in texts]

class DataProcessor:
    def __init__(self, raw_dir: str = "data/raw", processed_dir: str = "data/processed"):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.nlp = NLPProcessor()
        self.db = SessionLocal()

    def run_batch(self):
        print(f"Buscando archivos crudos en: {self.raw_dir}")
        for root, dirs, files in os.walk(self.raw_dir):
            for file in files:
                if file.endswith(".jsonl"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

    def _process_file(self, file_path: str):
        print(f"\n--- Procesando archivo: {file_path} ---")
        
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        if not records:
            print("El archivo está vacío.")
            return

        texts = [doc.get("texto_original", "") or doc.get("titulo", "") for doc in records]
        nlp_results = self.nlp.process_text_batch(texts)

        news_to_insert = []
        for doc, nlp_res in zip(records, nlp_results):
            try:
                fecha_str = doc.get("fecha")
                fecha_dt = datetime.fromisoformat(fecha_str) if fecha_str else datetime.utcnow()
                texto_original = doc.get("texto_original") or doc.get("titulo", "")
                
                # Heurística simple de inteligencia NLP causal
                texto_baja = texto_original.lower()
                sentimiento = nlp_res.get("label")
                if sentimiento == "positive":
                     if "record" in texto_baja or "high" in texto_baja or "up" in texto_baja: razon_ai = "Mención de alzas o récords históricos."
                     elif "beat" in texto_baja or "earnings" in texto_baja: razon_ai = "Superación de expectativas corporativas."
                     else: razon_ai = "Tono alcista general detectado semánticamente."
                elif sentimiento == "negative":
                     if "crash" in texto_baja or "drop" in texto_baja or "down" in texto_baja: razon_ai = "Alerta de caída o desplome estructural."
                     elif "inflation" in texto_baja or "rate" in texto_baja or "fed" in texto_baja: razon_ai = "Preocupación macroeconómica financiera."
                     else: razon_ai = "Semántica bajista detectada."
                else:
                     razon_ai = "Ausencia de marcadores emocionales fuertes."
                     
                new_record = ProcessedNews(
                    original_id=doc.get("id"),
                    fecha=fecha_dt,
                    titulo=doc.get("titulo"),
                    fuente=doc.get("fuente"),
                    texto_procesado=texto_original[:500] if texto_original else "",
                    sentimiento=sentimiento,
                    confianza=nlp_res.get("score"),
                    razonamiento=razon_ai
                )
                news_to_insert.append(new_record)
            except Exception as e:
                 print(f"Error creando Entidad ORM para guardar en Postgres: {e}")

        # Intento Batch Insert
        try:
             self.db.add_all(news_to_insert)
             self.db.commit()
             print(f"Lote insertado: {len(news_to_insert)} filas salvadas en PostgresSQL.")
             
             self._move_to_processed(file_path)
             
        except Exception as e:
             self.db.rollback()
             print(f"Error fatal ingresando datos en PosgreSQL: {e}. Descartando lote.")
             
    def _move_to_processed(self, file_path: str):
        rel_path = os.path.relpath(file_path, self.raw_dir)
        dest_path = os.path.join(self.processed_dir, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.move(file_path, dest_path)
        print(f"Archivo etiquetado y desplazado hacia: {dest_path}")
        
    def __del__(self):
        self.db.close()
