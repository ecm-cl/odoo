from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    # Los valores por defecto salen de medir glifo a glifo la salida real del
    # aplicativo Flex (PRUEBA_FLEX.pdf), que lleva años imprimiendo sobre
    # estos formularios. Son coordenadas del formulario, no de un banco en
    # particular: el formato de cheque chileno es el mismo en todos.

    vsg_check_printing = fields.Boolean(
        string="Imprimir cheques desde Odoo",
        help="Habilita la impresión de los cheques propios emitidos desde este diario "
             "sobre el formulario preimpreso del banco.",
    )
    vsg_check_place = fields.Char(
        string="Cheque: ciudad de emision",
        default="Santiago",
    )
    vsg_check_uppercase = fields.Boolean(
        string="Cheque: imprimir en mayúsculas",
        default=True,
    )
    vsg_check_amount_symbol = fields.Boolean(
        string="Cheque: anteponer símbolo de moneda",
        help="Marcar solo si el formulario del banco no trae el signo $ impreso.",
    )
    vsg_check_words_currency = fields.Boolean(
        string="Cheque: agregar la moneda al monto en palabras",
        help="En Chile se deja apagado: el formulario ya trae impreso 'PESOS M/L' "
             "y repetirlo sobra. Encender solo si el formulario no lo trae.",
    )
    vsg_check_date_split = fields.Boolean(
        string="Cheque: día, mes y año separados",
        help="Marcar cuando el formulario del banco tiene casilleros independientes "
             "para día, mes y año.",
    )
    vsg_check_month_name = fields.Boolean(
        string="Cheque: mes en palabras",
        help="Imprime el mes como nombre (enero) en lugar de número. El "
             "formulario chileno trae casilleros, así que va apagado.",
    )

    # --- geometria del formulario -------------------------------------
    vsg_check_width = fields.Float(string="Cheque: ancho (mm)", default=160.0)
    vsg_check_height = fields.Float(string="Cheque: alto (mm)", default=70.0)
    vsg_check_font_size = fields.Float(
        string="Cheque: tamaño de letra (pt)", default=12.0,
        help="Cuerpo del beneficiario, la fecha y el monto en números.")
    vsg_check_place_font_size = fields.Float(
        string="Cheque: tamaño de letra de la ciudad (pt)", default=10.0)
    vsg_check_words_font_size = fields.Float(
        string="Cheque: tamaño de letra del monto en palabras (pt)", default=9.0)

    # Todas las Y se miden hasta la LÍNEA BASE del texto, no hasta el borde
    # superior de la caja. Es como las mide Flex, y es lo único que no se
    # mueve cuando cambia el cuerpo de letra. El navegador posiciona por el
    # borde superior, así que hay que restarle el ascendente de la fuente.
    vsg_check_ascent = fields.Float(
        string="Cheque: ascendente de la fuente", default=0.9216,
        help="Distancia del borde superior de la línea a la línea base, en "
             "fracciones del cuerpo. 0,9216 es Arial con interlineado normal. "
             "Si todo el texto sale parejamente alto o bajo, se corrige aquí "
             "o con el ajuste vertical.",
    )

    # Calibración global: corrige la deriva de la impresora sin mover cada campo.
    vsg_check_offset_x = fields.Float(string="Cheque: ajuste horizontal (mm)", default=0.0)
    vsg_check_offset_y = fields.Float(string="Cheque: ajuste vertical (mm)", default=0.0)

    # Posiciones: X desde el borde izquierdo, Y hasta la línea base.
    vsg_check_place_x = fields.Float(string="Ciudad X (mm)", default=92.41)
    vsg_check_place_y = fields.Float(string="Ciudad: línea base Y (mm)", default=33.87)
    vsg_check_date_x = fields.Float(string="Fecha X (mm)", default=115.70)
    vsg_check_date_y = fields.Float(string="Fecha: línea base Y (mm)", default=33.87)
    vsg_check_day_x = fields.Float(string="Día X (mm)", default=115.70)
    vsg_check_month_x = fields.Float(string="Mes X (mm)", default=127.72)
    vsg_check_year_x = fields.Float(string="Año X (mm)", default=140.05)
    vsg_check_amount_x = fields.Float(string="Monto en números X (mm)", default=105.11)
    vsg_check_amount_y = fields.Float(
        string="Monto en números: línea base Y (mm)", default=25.40)
    vsg_check_words_x = fields.Float(string="Monto en letras X (mm)", default=29.97)
    vsg_check_words_y = fields.Float(
        string="Monto en letras: línea base Y (mm)", default=46.57)
    vsg_check_words_width = fields.Float(string="Monto en letras: ancho (mm)", default=131.0)
    vsg_check_words_line_height = fields.Float(
        string="Monto en letras: alto de línea (mm)", default=6.35)
    vsg_check_payee_x = fields.Float(string="Beneficiario X (mm)", default=29.97)
    vsg_check_payee_y = fields.Float(
        string="Beneficiario: línea base Y (mm)", default=40.56)
    vsg_check_payee_width = fields.Float(string="Beneficiario: ancho (mm)", default=113.0)

    # --- formularios con casilleros (el estándar chileno) ---------------
    vsg_check_cells = fields.Boolean(
        string="Cheque: formulario con casilleros", default=True,
        help="El formulario trae una casilla por dígito para el monto y la fecha. "
             "Cada dígito se imprime centrado en su casilla.",
    )
    vsg_check_date_cells = fields.Char(
        string="Casillas de fecha: centros X (mm)",
        default="116.88,121.82,128.90,133.80,141.23,146.17,151.11,156.05",
        help="Ocho valores separados por coma: día, día, mes, mes y los cuatro del año.",
    )
    vsg_check_cells_y = fields.Float(
        string="Casillas de fecha: línea base Y (mm)", default=33.87)
    vsg_check_year_preprinted = fields.Boolean(
        string="Cheque: el '20' del año viene impreso", default=True,
        help="Marcar cuando el formulario ya trae el 2 y el 0; solo se imprimen "
             "los dos últimos dígitos del año. Es lo que hace Flex. Se puede "
             "cambiar cheque por cheque desde el dialogo de impresión.",
    )
    vsg_check_amount_first_x = fields.Float(
        string="Casillas de monto: centro de la primera (mm)", default=106.29)
    vsg_check_amount_pitch = fields.Float(
        string="Casillas de monto: paso (mm)", default=4.975)
    vsg_check_amount_count = fields.Integer(
        string="Casillas de monto: cantidad", default=11)
    vsg_check_amount_cells_y = fields.Float(
        string="Casillas de monto: línea base Y (mm)", default=25.40)

    # --- rellenos de seguridad -----------------------------------------
    vsg_check_amount_fill = fields.Char(
        string="Casillas de monto: carácter de relleno", default="*", size=1,
        help="Se repite en las casillas que sobran a la derecha del monto para "
             "que no se pueda agregar un dígito. Vaciar para no rellenar.",
    )
    vsg_check_amount_thousands = fields.Boolean(
        string="Casillas de monto: separador de miles", default=True,
        help="El punto de miles se dibuja en la juntura entre dos casillas, sin "
             "ocupar una, que es como lo imprime Flex.",
    )
    vsg_check_words_fill = fields.Char(
        string="Monto en palabras: carácter de relleno", default="-", size=1,
        help="Completa la línea después del texto para que no se pueda agregar nada.",
    )
    vsg_check_payee_bold = fields.Boolean(
        string="Cheque: beneficiario en negrita", default=False,
        help="Flex lo imprime en redonda; el relieve lo da el cuerpo de 12 pt.")
    vsg_check_words2_x = fields.Float(
        string="Monto en palabras, 2a línea: X (mm)", default=14.10)
    vsg_check_words2_y = fields.Float(
        string="Monto en palabras, 2a línea: línea base Y (mm)", default=52.92)
    vsg_check_words2_width = fields.Float(
        string="Monto en palabras, 2a línea: ancho (mm)", default=57.2,
        help="Termina antes de la leyenda PESOS M/L impresa en el formulario.")

    # --- hoja de impresión ---------------------------------------------
    # El cheque no se imprime solo: va sobre una hoja cuyo tamaño es el que
    # queda configurado en la impresora. Flex usa 98 x 190 mm en vertical, con
    # el lado corto hacia el alimentador, y el cheque apoyado en una esquina.
    vsg_check_sheet_vertical = fields.Boolean(
        string="Cheque: hoja vertical (lado corto al alimentador)",
        default=True,
        help="Gira la página del PDF para que el dialogo de impresión muestre la "
             "hoja en vertical, igual que el aplicativo Flex. El contenido sale "
             "identico; solo cambia como se alimenta el papel.",
    )
    vsg_check_sheet_long = fields.Float(
        string="Hoja: largo (mm)", default=190.5,
        help="Lado largo de la hoja. Al imprimir en vertical queda de arriba "
             "a abajo. Flex usa 190,5 mm (7,5 pulgadas).",
    )
    vsg_check_sheet_short = fields.Float(
        string="Hoja: ancho (mm)", default=98.42,
        help="Lado corto de la hoja, el que entra primero al alimentador. "
             "Flex usa 98,42 mm (3,875 pulgadas).",
    )
    vsg_check_sheet_x = fields.Float(
        string="Hoja: posición X del cheque (mm)", default=0.0,
        help="Distancia desde el borde izquierdo de la hoja hasta el borde "
             "izquierdo del cheque. Se suma a todas las coordenadas.",
    )
    vsg_check_sheet_y = fields.Float(
        string="Hoja: posición Y del cheque (mm)", default=0.0,
        help="Distancia desde el borde superior de la hoja hasta el borde "
             "superior del cheque. Se suma a todas las coordenadas.",
    )

    # --- tachado de 'a la orden de' y 'o al portador' ---------------------
    # Un cheque nominativo tacha las dos leyendas; uno a la orden solo tacha
    # 'o al portador'; uno al portador no tacha nada.
    vsg_check_endorsement_default = fields.Selection(
        [("nominativo", "Nominativo"),
         ("orden", "A la orden"),
         ("portador", "Al portador")],
        string="Cheque: tipo por defecto", default="nominativo",
    )
    vsg_check_strike_char = fields.Char(
        string="Tachado: carácter", default="*", size=1,
        help="Se repite hasta cubrir el ancho declarado, como lo hace Flex.",
    )
    vsg_check_strike_font = fields.Float(string="Tachado: tamaño de letra (pt)", default=8.0)
    vsg_check_strike_order_x = fields.Float(
        string="Tachado 'a la orden de': X (mm)", default=13.73)
    vsg_check_strike_order_y = fields.Float(
        string="Tachado 'a la orden de': línea base Y (mm)", default=42.80)
    vsg_check_strike_order_width = fields.Float(
        string="Tachado 'a la orden de': ancho (mm)", default=15.70)
    vsg_check_strike_bearer_x = fields.Float(
        string="Tachado 'o al portador': X (mm)", default=141.81)
    vsg_check_strike_bearer_y = fields.Float(
        string="Tachado 'o al portador': línea base Y (mm)", default=44.80)
    vsg_check_strike_bearer_width = fields.Float(
        string="Tachado 'o al portador': ancho (mm)", default=15.80)

    # --- cruzado ---------------------------------------------------------
    vsg_check_crossed_default = fields.Boolean(
        string="Cheque: cruzado por defecto", default=True)
    vsg_check_cross_x = fields.Float(string="Cruzado: X (mm)", default=13.4)
    vsg_check_cross_y = fields.Float(string="Cruzado: Y (mm)", default=16.6)
    vsg_check_cross_width = fields.Float(
        string="Cruzado: avance a lo largo del cheque (mm)", default=27.0)
    vsg_check_cross_height = fields.Float(
        string="Cruzado: avance a lo alto del cheque (mm)", default=52.0)
    vsg_check_cross_gap = fields.Float(string="Cruzado: separacion entre rayas (mm)", default=3.5)
    vsg_check_cross_thickness = fields.Float(string="Cruzado: grosor (mm)", default=0.4)

    @api.model
    def _vsg_check_position_fields(self):
        """Campos de coordenadas, usados por la grilla de calibración."""
        return [
            ("place", "Ciudad"),
            ("date", "Fecha"),
            ("amount", "Monto en números"),
            ("words", "Monto en letras"),
            ("payee", "Beneficiario"),
        ]
