# Sistema predictivo de platos de fondo — Ñemby

El sistema está orientado a un comedor/negocio que prepara y vende almuerzos. La unidad de pronóstico es la porción de cada plato, no la venta de ingredientes sueltos.

Archivos:
- dashboard.py: dashboard Streamlit para pronosticar porciones y calcular ingredientes a comprar desde recetas.
- schema.sql: estructura SQL relacional.
- almuerzos_nemby.db: base SQLite inicializada.
- control_almuerzos_excel.xlsx: hojas Platos, Recetas, Ingredientes, Ventas y Resumen.
- requirements.txt: dependencias.

Ejecución:
1. `pip install -r requirements.txt`
2. `streamlit run dashboard.py`

El pronóstico combina promedio de ventas de las últimas ocurrencias del mismo día de la semana (70%) y promedio reciente de los últimos 28 registros (30%). Es una línea base y necesita ventas reales. Completa recetas y stock para obtener cantidades de compra. Registra sobrantes para reducir sobreproducción.

Importante: las cantidades de recetas, precios y costos deben ser introducidos por el negocio. Los nombres iniciales de platos son tentativos y deben confirmarse.
