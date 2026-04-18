# 🚀 Real-Time Market Intelligence System (RT-MIS)

Este es un sistema de ingeniería de datos de grado profesional diseñado para la ingesta, procesamiento de lenguaje natural (NLP) y validación de sentimiento financiero en tiempo real. 

El proyecto demuestra habilidades avanzadas en **Data Engineering**, **NLP pipelines** y **Backtesting de Mercados**.

---

## 🏗️ Arquitectura del Sistema

El flujo de datos sigue un patrón ETL (Extract, Transform, Load) optimizado para baja latencia:

1.  **Ingestión (Extract):** Módulos robustos que conectan con `NewsAPI` (Noticias globales) y `yfinance` (Datos bursátiles intradía). Implementa patrones de reintento con *Exponential Backoff*.
2.  **Procesamiento (Transform - IA):** 
    *   **FinBERT:** Modelo Transformer especializado en finanzas que clasifica el sentimiento.
    *   **The Analyst (Gemini LLM):** Generación de resúmenes ejecutivos narrativos sobre tendencias de mercado.
    *   **Validador Pro:** Motor de backtest que correlaciona el sentimiento con el movimiento del Nasdaq (QQQ) en una ventana de 4 horas.
3.  **Almacenamiento (Load):** Base de datos relacional `PostgreSQL` gestionada mediante `SQLAlchemy` (ORM).
4.  **Visualización (Serving):** Dashboard interactivo en `Streamlit` para usuarios técnicos y de negocio.

---

## 📊 Características Principales

*   **Validación Cruzada Intradía:** Comprobación automática de si la IA "acertó" el movimiento del precio 4 horas después de la noticia.
*   **Filtrado de Alta Confianza:** KPI de éxito real basado únicamente en señales con >90% de certeza.
*   **Identificación de Tickers:** Extracción inteligente de empresas (NVDA, AAPL, etc.) para validación específica.
*   **Narrativa Ejecutiva:** Resúmenes generados por LLM que explican el "por qué" detrás de los datos.

---

## 🛠️ Tecnologías Utilizadas

*   **Lenguaje:** Python 3.10+
*   **IA/NLP:** FinBERT (HuggingFace), Google Gemini (Generative AI).
*   **Database:** PostgreSQL + SQLAlchemy.
*   **Finanzas:** yfinance (Yahoo Finance API).
*   **Dashboard:** Streamlit + Altair Charts.

---

## 🚀 Instalación y Ejecución

### 1. Requisitos Previos
*   PostgreSQL instalado y corriendo.
*   API Keys de [NewsAPI](https://newsapi.org/) y [Google AI Studio](https://aistudio.google.com/).

### 2. Configuración del Entorno
```bash
# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Variables de Entorno
Crea un archivo `.env` basado en el `.env.example`:
```env
NEWSAPI_KEY=tu_clave_newsapi
GEMINI_API_KEY=tu_clave_gemini
DB_NAME=mercado_rt
DB_USER=tu_usuario
DB_PASSWORD=tu_password
```

### 4. Flujo de Ejecución
```bash
# 1. Ingesta de noticias
python src/pipeline/run_ingestion.py

# 2. Procesamiento e Inyección a DB
python src/pipeline/run_processing.py

# 3. Lanzar Dashboard
streamlit run ui/app.py
```

---
**Desarrollado como proyecto de Portafolio Senior en Data Engineering.**
