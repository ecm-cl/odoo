# Valsegur Legacy Fields

Addon mínimo para conservar los valores originales de cargas contables históricas.

## Alcance

- Extiende `account.move` y `account.move.line` con campos `x_legacy_*`.
- Agrupa en Exportar los campos fuente con el prefijo `Origen:` y los campos
  técnicos creados para el proceso con el prefijo `Migración:`.
- Agrega todos los campos a los selectores opcionales de columnas y a las
  búsquedas de Asientos contables y Apuntes contables.
- Agrega un identificador idempotente por asiento.
- Agrega `account.legacy.import.batch` para registrar archivo, hoja, SHA-256 y controles contables del lote.
- Relaciona cada asiento con su lote mediante `x_legacy_batch_id`.
- Conserva los códigos y textos originales aunque también se homologuen a campos estándar.
- No importa archivos, no crea diarios y no publica asientos.

Los campos quedan disponibles en el importador y exportador estándar de Odoo.
Cada campo usa la misma etiqueta en búsqueda, exportación, selector de columnas
y encabezado. Las etiquetas comienzan con `Migración:` u `Origen:` y conservan
entre paréntesis el nombre de la columna fuente. Los lotes se administran desde Contabilidad → Configuración →
Contabilidad → Lotes de migración.
