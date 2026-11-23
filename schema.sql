
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS ingredientes(
 ingrediente_id INTEGER PRIMARY KEY AUTOINCREMENT,
 nombre TEXT NOT NULL UNIQUE, unidad TEXT NOT NULL,
 costo_unitario REAL NOT NULL DEFAULT 0,
 stock_actual REAL NOT NULL DEFAULT 0,
 stock_seguridad REAL NOT NULL DEFAULT 0,
 proveedor TEXT, perecedero INTEGER NOT NULL DEFAULT 1,
 activo INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS platos(
 plato_id INTEGER PRIMARY KEY AUTOINCREMENT,
 nombre TEXT NOT NULL UNIQUE,
 precio_venta REAL NOT NULL DEFAULT 0,
 costo_estimado REAL NOT NULL DEFAULT 0,
 categoria TEXT DEFAULT 'Plato de fondo',
 activo INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS recetas(
 receta_id INTEGER PRIMARY KEY AUTOINCREMENT,
 plato_id INTEGER NOT NULL REFERENCES platos(plato_id),
 ingrediente_id INTEGER NOT NULL REFERENCES ingredientes(ingrediente_id),
 cantidad_por_porcion REAL NOT NULL CHECK(cantidad_por_porcion>0),
 UNIQUE(plato_id,ingrediente_id)
);
CREATE TABLE IF NOT EXISTS ventas_almuerzo(
 venta_id INTEGER PRIMARY KEY AUTOINCREMENT,
 fecha TEXT NOT NULL,
 plato_id INTEGER NOT NULL REFERENCES platos(plato_id),
 porciones_vendidas INTEGER NOT NULL CHECK(porciones_vendidas>=0),
 precio_unitario REAL NOT NULL DEFAULT 0,
 sobrantes INTEGER NOT NULL DEFAULT 0,
 canal TEXT DEFAULT 'local'
);
CREATE TABLE IF NOT EXISTS produccion(
 produccion_id INTEGER PRIMARY KEY AUTOINCREMENT,
 fecha TEXT NOT NULL,
 plato_id INTEGER NOT NULL REFERENCES platos(plato_id),
 porciones_preparadas INTEGER NOT NULL,
 porciones_no_vendidas INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS compras_ingredientes(
 compra_id INTEGER PRIMARY KEY AUTOINCREMENT,
 fecha TEXT NOT NULL,
 ingrediente_id INTEGER NOT NULL REFERENCES ingredientes(ingrediente_id),
 cantidad REAL NOT NULL,
 costo_unitario REAL NOT NULL,
 proveedor TEXT
);
CREATE INDEX IF NOT EXISTS idx_ventas_almuerzo_fecha ON ventas_almuerzo(fecha,plato_id);
CREATE INDEX IF NOT EXISTS idx_compras_ing_fecha ON compras_ingredientes(fecha,ingrediente_id);

-- Catálogo tentativo basado en la lista manuscrita. Confirmar nombres y platos.
INSERT OR IGNORE INTO platos(nombre,precio_venta) VALUES
 ('Carne con arroz',0),('Pollo con puré',0),('Choclo con carne',0),
 ('Ensalada con carne',0);

-- Ingredientes iniciales: completar unidades, precios y existencias reales.
INSERT OR IGNORE INTO ingredientes(nombre,unidad) VALUES
 ('Arroz','kg'),('Carne','kg'),('Papa','kg'),('Choclo','unidad'),
 ('Pollo','kg'),('Lechuga','unidad'),('Tomate','kg'),('Aceite','litro'),
 ('Cebolla','kg'),('Zanahoria','kg');

-- Recetas: no se precargan cantidades para evitar asumir recetas que no fueron confirmadas.
