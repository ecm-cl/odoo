from odoo import fields, models


class AccountLegacyImportBatch(models.Model):
    _name = "account.legacy.import.batch"
    _description = "Lote de migración contable legado"
    _order = "prepared_at desc, id desc"
    _check_company_auto = True

    name = fields.Char(
        string="Identificador del lote",
        required=True,
        copy=False,
        index=True,
        help=(
            "Identificador operativo del lote con la estructura "
            "<EMPRESA>-<AÑO>-<ALCANCE>-<SECUENCIA>. "
            "Ejemplo: VALSEGUR-2025-PILOTO-002."
        ),
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Empresa",
        required=True,
        default=lambda self: self.env.company,
        index=True,
        ondelete="restrict",
    )
    source_filename = fields.Char(
        string="Archivo fuente",
        required=True,
        copy=False,
        help=(
            "Nombre exacto del archivo fuente, incluida su extensión. "
            "No incluye la ruta local del computador."
        ),
    )
    source_sheet = fields.Char(
        string="Hoja fuente",
        copy=False,
        help="Nombre exacto de la hoja utilizada dentro del archivo fuente.",
    )
    source_sha256 = fields.Char(
        string="SHA-256",
        required=True,
        copy=False,
        index=True,
        size=64,
        help=(
            "Huella SHA-256 completa, de 64 caracteres hexadecimales, "
            "calculada sobre los bytes originales del archivo fuente."
        ),
    )
    source_size = fields.Integer(
        string="Tamaño del archivo (bytes)",
        copy=False,
        help="Tamaño exacto del archivo fuente en bytes.",
    )
    source_move_count = fields.Integer(
        string="Comprobantes fuente",
        copy=False,
        help="Cantidad de comprobantes completos incluidos en el lote.",
    )
    source_line_count = fields.Integer(
        string="Líneas fuente",
        copy=False,
        help="Cantidad de líneas contables incluidas en el lote.",
    )
    source_debit_total = fields.Monetary(
        string="Debe fuente",
        currency_field="currency_id",
        copy=False,
        help="Suma de DEBE de todas las líneas incluidas en el lote.",
    )
    source_credit_total = fields.Monetary(
        string="Haber fuente",
        currency_field="currency_id",
        copy=False,
        help="Suma de HABER de todas las líneas incluidas en el lote.",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )
    prepared_at = fields.Datetime(
        string="Preparado el",
        required=True,
        default=fields.Datetime.now,
        copy=False,
        help="Fecha y hora en que se preparó el lote para importación.",
    )
    notes = fields.Text(string="Notas", copy=False)
    move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="x_legacy_batch_id",
        string="Asientos migrados",
        readonly=True,
    )

    _name_company_unique = models.Constraint(
        "UNIQUE(company_id, name)",
        "El identificador del lote debe ser único por empresa.",
    )
    _sha256_format = models.Constraint(
        "CHECK(source_sha256 ~ '^[0-9A-Fa-f]{64}$')",
        "El SHA-256 debe contener exactamente 64 caracteres hexadecimales.",
    )
    _non_negative_controls = models.Constraint(
        "CHECK(source_size >= 0 AND source_move_count >= 0 AND source_line_count >= 0 "
        "AND source_debit_total >= 0 AND source_credit_total >= 0)",
        "Los controles numéricos del lote no pueden ser negativos.",
    )
