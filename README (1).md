# Mi cocina + PixelRAG
Python 3.11 o 3.12 recomendado. Desde la carpeta del proyecto:

    python -m pip install -r requirements.txt
    python -m playwright install chromium
    python -m uvicorn app:app --host 127.0.0.1 --port 8000

Abrir http://127.0.0.1:8000/ (no abrir el HTML directamente). La primera consulta descarga CLIP y SmolVLM. No requiere claves API. El servidor recibe el estado actual del navegador y lo renderiza en Chromium para recuperar imágenes. El almacenamiento local de una URL anterior no se migra automáticamente. Las respuestas visuales pueden contener errores numéricos. CLIP funciona mejor con preguntas en inglés. Prototipo local, no exponer a Internet. Inferencia no probada en este entorno.
