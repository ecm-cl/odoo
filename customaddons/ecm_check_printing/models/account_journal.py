from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    vsg_check_printing = fields.Boolean(
        string="Imprimir cheques desde Odoo",
        help="Habilita la impresion de los cheques propios emitidos desde este diario "
             "sobre el formulario preimpreso del banco.",
    )
    vsg_check_place = fields.Char(
        string="Cheque: ciudad de emision",
        default="Santiago",
    )
    vsg_check_uppercase = fields.Boolean(
        string="Cheque: imprimir en mayusculas",
        default=True,
    )
    vsg_check_amount_symbol = fields.Boolean(
        string="Cheque: anteponer simbolo de moneda",
        help="Marcar solo si el formulario del banco no trae el signo $ impreso.",
    )
    vsg_check_words_currency = fields.Boolean(
        string="Cheque: agregar la moneda al monto en palabras",
        help="En Chile se deja apagado: el formulario ya trae impreso 'PESOS M/L' "
             "y repetirlo sobra. Encender solo si el formulario no lo trae.",
    )
    vsg_check_date_split = fields.Boolean(
        string="Cheque: dia, mes y anio separados",
        help="Marcar cuando el formulario del banco tiene casilleros independientes "
             "para dia, mes y anio.",
    )
    vsg_check_month_name = fields.Boolean(
        string="Cheque: mes en palabras",
        default=True,
        help="Imprime el mes como nombre (enero) en lugar de numero.",
    )

    # --- geometria del formulario -------------------------------------
    vsg_check_width = fields.Float(string="Cheque: ancho (mm)", default=180.0)
    vsg_check_height = fields.Float(string="Cheque: alto (mm)", default=85.0)
    vsg_check_font_size = fields.Float(string="Cheque: tamanio de letra (pt)", default=11.0)

    # Calibracion global: corrige la deriva de la impresora sin mover cada campo.
    vsg_check_offset_x = fields.Float(string="Cheque: ajuste horizontal (mm)", default=0.0)
    vsg_check_offset_y = fields.Float(string="Cheque: ajuste vertical (mm)", default=0.0)

    # Posiciones de cada campo, medidas desde el borde superior izquierdo.
    vsg_check_place_x = fields.Float(string="Ciudad X (mm)", default=25.0)
    vsg_check_place_y = fields.Float(string="Ciudad Y (mm)", default=18.0)
    vsg_check_date_x = fields.Float(string="Fecha X (mm)", default=95.0)
    vsg_check_date_y = fields.Float(string="Fecha Y (mm)", default=18.0)
    vsg_check_day_x = fields.Float(string="Dia X (mm)", default=95.0)
    vsg_check_month_x = fields.Float(string="Mes X (mm)", default=115.0)
    vsg_check_year_x = fields.Float(string="Anio X (mm)", default=145.0)
    vsg_check_amount_x = fields.Float(string="Monto en numeros X (mm)", default=140.0)
    vsg_check_amount_y = fields.Float(string="Monto en numeros Y (mm)", default=32.0)
    vsg_check_words_x = fields.Float(string="Monto en letras X (mm)", default=20.0)
    vsg_check_words_y = fields.Float(string="Monto en letras Y (mm)", default=42.0)
    vsg_check_words_width = fields.Float(string="Monto en letras: ancho (mm)", default=140.0)
    vsg_check_words_line_height = fields.Float(string="Monto en letras: alto de linea (mm)", default=6.0)
    vsg_check_payee_x = fields.Float(string="Beneficiario X (mm)", default=20.0)
    vsg_check_payee_y = fields.Float(string="Beneficiario Y (mm)", default=55.0)
    vsg_check_payee_width = fields.Float(string="Beneficiario: ancho (mm)", default=140.0)

    # --- formularios con casilleros (el estandar chileno) ---------------
    vsg_check_cells = fields.Boolean(
        string="Cheque: formulario con casilleros",
        help="El formulario trae una casilla por digito para el monto y la fecha. "
             "Cada digito se imprime centrado en su casilla.",
    )
    vsg_check_date_cells = fields.Char(
        string="Casillas de fecha: centros X (mm)",
        default="112.5,117.6,124.6,129.6,136.7,141.6,146.6,151.6",
        help="Ocho valores separados por coma: dia, dia, mes, mes y los cuatro del anio.",
    )
    vsg_check_cells_y = fields.Float(string="Casillas de fecha: Y (mm)", default=14.5)
    vsg_check_year_preprinted = fields.Boolean(
        string="Cheque: el '20' del anio viene impreso",
        help="Marcar cuando el formulario ya trae el 2 y el 0; solo se imprimen "
             "los dos ultimos digitos del anio.",
    )
    vsg_check_amount_first_x = fields.Float(
        string="Casillas de monto: centro de la primera (mm)", default=101.6)
    vsg_check_amount_pitch = fields.Float(
        string="Casillas de monto: paso (mm)", default=5.0)
    vsg_check_amount_count = fields.Integer(
        string="Casillas de monto: cantidad", default=11)
    vsg_check_amount_cells_y = fields.Float(
        string="Casillas de monto: Y (mm)", default=6.0)

    # --- rellenos de seguridad -----------------------------------------
    vsg_check_amount_fill = fields.Char(
        string="Casillas de monto: caracter de relleno", default="*", size=1,
        help="Se repite en las casillas que sobran a la derecha del monto para "
             "que no se pueda agregar un digito. Vaciar para no rellenar.",
    )
    vsg_check_amount_thousands = fields.Boolean(
        string="Casillas de monto: separador de miles", default=True,
        help="El punto de miles ocupa su propia casilla, como en el formato manual.",
    )
    vsg_check_words_fill = fields.Char(
        string="Monto en palabras: caracter de relleno", default="-", size=1,
        help="Completa la linea despues del texto para que no se pueda agregar nada.",
    )
    vsg_check_payee_bold = fields.Boolean(
        string="Cheque: beneficiario en negrita", default=True)
    vsg_check_words2_x = fields.Float(string="Monto en palabras, 2a linea: X (mm)", default=12.0)
    vsg_check_words2_y = fields.Float(string="Monto en palabras, 2a linea: Y (mm)", default=36.8)
    vsg_check_words2_width = fields.Float(
        string="Monto en palabras, 2a linea: ancho (mm)", default=53.0,
        help="Termina antes de la leyenda PESOS M/L impresa en el formulario.")

    @api.model
    def _vsg_check_position_fields(self):
        """Campos de coordenadas, usados por la grilla de calibracion."""
        return [
            ("place", "Ciudad"),
            ("date", "Fecha"),
            ("amount", "Monto en numeros"),
            ("words", "Monto en letras"),
            ("payee", "Beneficiario"),
        ]
