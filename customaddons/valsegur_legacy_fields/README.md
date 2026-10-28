# Valsegur Legacy Fields

Addon mínimo para conservar los valores originales de cargas contables históricas.

## Alcance

- Extiende `account.move` y `account.move.line` con campos `x_legacy_*`.
- Conserva las etiquetas originales del XLS (`NUMERO`, `TIP_COMP`, `LINEA`, etc.).
- Agrega un identificador idempotente por asiento.
- Agrega `account.legacy.import.batch` para registrar archivo, hoja, SHA-256 y controles contables del lote.
- Relaciona cada asiento con su lote mediante `x_legacy_batch_id`.
- Conserva los códigos y textos originales aunque también se homologuen a campos estándar.
- No importa archivos, no crea diarios y no publica asientos.

Los campos quedan disponibles en el importador y exportador estándar de Odoo. Los lotes se administran desde Contabilidad → Configuración → Contabilidad → Lotes de migración.
