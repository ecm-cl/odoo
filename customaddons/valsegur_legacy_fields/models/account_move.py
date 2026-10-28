from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    x_legacy_batch_id = fields.Many2one(
        comodel_name="account.legacy.import.batch",
        string="Lote de migración",
        copy=False,
        index=True,
        check_company=True,
        ondelete="restrict",
        help=(
            "Registro que documenta el lote de origen de este asiento. "
            "Conserva la empresa, el nombre exacto del archivo, la hoja, "
            "el SHA-256 completo y los controles contables del lote."
        ),
    )
    x_legacy_key = fields.Char(
        string="Identificador de asiento migrado",
        copy=False,
        index=True,
        help=(
            "Identificador generado durante la migración con la estructura "
            "<empresa>_<año>_<TIP_COMP>_<NUMERO>. "
            "Ejemplo: valsegur_2025_T_9090. Permite detectar importaciones "
            "duplicadas y rastrear el asiento hasta el comprobante de origen."
        ),
    )
    x_legacy_numero = fields.Char(
        string="NUMERO",
        copy=False,
        index=True,
        help="Valor original de la columna NUMERO.",
    )
    x_legacy_tip_comp = fields.Char(
        string="TIP_COMP",
        copy=False,
        index=True,
        help="Valor original de TIP_COMP: T, I o E.",
    )
    x_legacy_ano_mov = fields.Integer(
        string="ANO_MOV",
        copy=False,
        help="Valor original de la columna ANO_MOV.",
    )

    _legacy_key_unique = models.Constraint(
        "UNIQUE(company_id, x_legacy_key)",
        "El identificador de asiento migrado debe ser único por empresa.",
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    x_legacy_linea = fields.Integer(
        string="LINEA",
        copy=False,
        help="Valor original de la columna LINEA.",
    )
    x_legacy_cuenta = fields.Char(
        string="CUENTA",
        copy=False,
        index=True,
        help="Código original de la columna CUENTA.",
    )
    x_legacy_cta_item = fields.Char(
        string="CTA_ITEM",
        copy=False,
        index=True,
        help="Valor original de CTA_ITEM, sin reemplazarlo por el partner homologado.",
    )
    x_legacy_dig_ver = fields.Char(
        string="DIG_VER",
        copy=False,
        help="Valor original de DIG_VER, incluso cuando el RUT haya sido corregido.",
    )
    x_legacy_vencimiento = fields.Char(
        string="VENCTO",
        copy=False,
        help="Representación original de VENCTO antes de normalizar date_maturity.",
    )
    x_legacy_centro = fields.Char(
        string="CENTRO",
        copy=False,
        index=True,
        help="Valor original de CENTRO, aun cuando exista homologación analítica.",
    )
    x_legacy_tip_anal = fields.Char(
        string="TIP_ANAL",
        copy=False,
        help="Valor original de TIP_ANAL.",
    )
    x_legacy_tip_docu = fields.Char(
        string="TIP_DOCU",
        copy=False,
        help="Valor original de TIP_DOCU.",
    )
    x_legacy_num_docu = fields.Char(
        string="NUM_DOCU",
        copy=False,
        index=True,
        help="Valor original de NUM_DOCU guardado como texto.",
    )
    x_legacy_tip_glosa = fields.Char(
        string="TIP_GLOSA",
        copy=False,
        help="Valor original de TIP_GLOSA.",
    )
    x_legacy_ano = fields.Integer(
        string="ANO",
        copy=False,
        help="Valor original de ANO.",
    )
    x_legacy_tip_tabla = fields.Char(
        string="TIP_TABLA",
        copy=False,
        help="Valor original de TIP_TABLA.",
    )
    x_legacy_num_adic = fields.Char(
        string="NUM_ADIC",
        copy=False,
        help="Valor original de NUM_ADIC.",
    )
    x_legacy_cod_mon = fields.Char(
        string="COD_MON",
        copy=False,
        help="Valor original de COD_MON, aun cuando exista currency_id.",
    )
    x_legacy_paridad = fields.Float(
        string="PARIDAD",
        copy=False,
        digits=(16, 6),
        help="Valor original de PARIDAD, sin inferir una tasa de cambio.",
    )
    x_legacy_bimfol = fields.Char(
        string="BIMFOL",
        copy=False,
        help="Valor original de BIMFOL.",
    )
    x_legacy_tip_bim = fields.Char(
        string="TIP_BIM",
        copy=False,
        help="Valor original de TIP_BIM.",
    )
    x_legacy_cambio = fields.Char(
        string="CAMBIO",
        copy=False,
        help="Valor original de CAMBIO; no representa por sí solo un tipo de cambio.",
    )
    x_legacy_af_flujo = fields.Char(
        string="AF_FLUJO",
        copy=False,
        help="Valor original de AF_FLUJO.",
    )
    x_legacy_debe_ad = fields.Float(
        string="DEBE_AD",
        copy=False,
        digits=(16, 6),
        help="Valor original de DEBE_AD.",
    )
    x_legacy_haber_ad = fields.Float(
        string="HABER_AD",
        copy=False,
        digits=(16, 6),
        help="Valor original de HABER_AD.",
    )
    x_legacy_descrip = fields.Char(
        string="DESCRIP",
        copy=False,
        help="Valor original de DESCRIP; no sobrescribe el nombre maestro de la cuenta.",
    )
    x_legacy_nombre = fields.Char(
        string="NOMBRE",
        copy=False,
        help="Valor original de NOMBRE; no sobrescribe automáticamente el partner.",
    )
