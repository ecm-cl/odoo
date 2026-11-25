import logging
import textwrap

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:  # pragma: no cover
    num2words = None

MONTHS_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


class L10nLatamCheck(models.Model):
    _inherit = "l10n_latam.check"

    def _vsg_journal(self):
        """Diario bancario que emite el cheque propio."""
        self.ensure_one()
        return self.payment_id.journal_id

    def _vsg_amount_in_words(self):
        """Monto en letras en espaniol, sin decimales cuando la moneda no los usa."""
        self.ensure_one()
        if num2words is None:
            raise UserError(_(
                "Falta la libreria 'num2words'; no se puede imprimir el monto en letras."
            ))
        currency = self.currency_id or self.company_id.currency_id
        decimals = currency.decimal_places
        amount = self.amount or 0.0
        integral = int(amount)
        words = self._vsg_apocope(num2words(integral, lang="es"))
        if not self._vsg_journal().vsg_check_words_currency:
            # El formulario chileno ya trae impreso "PESOS M/L"
            return words
        unit = self._vsg_plural(currency.currency_unit_label or "Peso", integral).lower()
        # En espaniol "millon" y "millones" exigen la preposicion: "dos millones de pesos".
        link = "de " if words.split()[-1] in ("millon", "millones", "millón") else ""
        text = "%s %s%s" % (words, link, unit)
        if decimals:
            fractional = int(round((amount - integral) * (10 ** decimals)))
            if fractional:
                subunit = self._vsg_plural(
                    currency.currency_subunit_label or "Centavo", fractional
                )
                text = "%s con %s %s" % (
                    text, num2words(fractional, lang="es"), subunit,
                )
        return text.strip()

    def _vsg_date_digit_cells(self):
        """Digitos de la fecha con la X de su casilla: [(x_mm, digito), ...].

        El formulario chileno trae ocho casillas: d d m m a a a a. Cuando el
        banco ya imprimio el '20' del anio solo se llenan las dos ultimas.
        """
        self.ensure_one()
        journal = self._vsg_journal()
        try:
            xs = [float(v) for v in (journal.vsg_check_date_cells or "").split(",")]
        except ValueError:
            raise UserError(_(
                "Las casillas de fecha del diario %s no son una lista de numeros "
                "separados por coma.", journal.display_name))
        if len(xs) != 8:
            raise UserError(_(
                "El diario %s debe declarar ocho casillas de fecha y declara %s.",
                journal.display_name, len(xs)))
        partes = self._vsg_date_parts()
        digitos = partes["day"] + ("%02d" % int(partes["numeric_month"])) + partes["year"]
        pares = list(zip(xs, digitos))
        if journal.vsg_check_year_preprinted:
            pares = pares[:4] + pares[6:]
        return pares

    def _vsg_amount_digit_cells(self):
        """Digitos del monto en sus casillas, como se llena un cheque a mano.

        El numero se alinea a la IZQUIERDA, el punto de miles ocupa una casilla
        propia y las casillas sobrantes se rellenan con un asterisco para que no
        se pueda agregar una cifra despues.
        """
        self.ensure_one()
        journal = self._vsg_journal()
        cantidad = journal.vsg_check_amount_count or 0
        entero = int(abs(self.amount or 0.0))
        texto = "{:,}".format(entero).replace(",", ".") if journal.vsg_check_amount_thousands             else str(entero)
        if len(texto) > cantidad:
            # sin separadores todavia puede caber
            texto = str(entero)
        if len(texto) > cantidad:
            raise UserError(_(
                "El monto %s no cabe en las %s casillas del diario %s.",
                texto, cantidad, journal.display_name))
        relleno = (journal.vsg_check_amount_fill or "")[:1]
        if relleno:
            texto = texto + relleno * (cantidad - len(texto))
        paso = journal.vsg_check_amount_pitch or 5.0
        primera = journal.vsg_check_amount_first_x
        return [(primera + i * paso, c) for i, c in enumerate(texto)]

    def _vsg_amount_figures(self):
        """Monto en cifras con formato chileno: 17.000.000, sin espacio duro.

        No se usa el widget monetario de QWeb porque inserta un espacio duro
        que wkhtmltopdf deja como basura, y porque toma los separadores del
        idioma de la sesion en lugar de los de Chile.
        """
        self.ensure_one()
        currency = self.currency_id or self.company_id.currency_id
        decimals = currency.decimal_places
        amount = self.amount or 0.0
        entera = "{:,.0f}".format(int(amount)).replace(",", ".")
        if not decimals:
            texto = entera
        else:
            resto = abs(amount) - int(abs(amount))
            texto = "%s,%s" % (entera, ("%.*f" % (decimals, resto))[2:])
        journal = self._vsg_journal()
        if journal.vsg_check_amount_symbol:
            texto = "%s%s" % (currency.symbol or "$", texto)
        return texto

    @staticmethod
    def _vsg_apocope(words):
        """Aplica la apocope del espaniol: 'uno mil' se dice 'un mil'.

        num2words no la aplica y en un cheque la redaccion importa. Se trabaja
        por palabras para no depender de expresiones regulares.
        """
        forms = {"uno": "un", "veintiuno": "veintiún"}
        tokens = words.split()
        for i, token in enumerate(tokens):
            if token not in forms:
                continue
            is_last = i == len(tokens) - 1
            before_mil = not is_last and tokens[i + 1] == "mil"
            if is_last or before_mil:
                tokens[i] = forms[token]
        return " ".join(tokens)

    @staticmethod
    def _vsg_plural(label, quantity):
        """Pluraliza la etiqueta de la moneda: Odoo la guarda en singular."""
        label = (label or "").strip()
        if quantity == 1 or not label or label.lower().endswith("s"):
            return label
        return label + ("es" if label[-1].lower() not in "aeiou" else "s")

    def _vsg_words_rows(self):
        """Lineas del monto en palabras, ya rellenas: [(x, y, ancho, texto)].

        El formulario tiene dos renglones utiles. El texto ocupa lo que
        necesita y el resto se completa con guiones, igual que al llenarlo a
        mano, para que no se pueda agregar nada despues.
        """
        self.ensure_one()
        journal = self._vsg_journal()
        cuerpo = self._vsg_words_font()
        base = journal.vsg_check_font_size or 11.0
        char_mm = self._vsg_char_mm() * cuerpo / base
        renglones = [
            (journal.vsg_check_words_x, journal.vsg_check_words_y,
             journal.vsg_check_words_width),
            (journal.vsg_check_words2_x, journal.vsg_check_words2_y,
             journal.vsg_check_words2_width),
        ]
        palabras = self._vsg_amount_in_words().split()
        relleno = (journal.vsg_check_words_fill or "")[:1]
        filas, i = [], 0
        for x, y, ancho in renglones:
            if ancho <= 0:
                continue
            cupo = max(int(ancho / char_mm), 4)
            linea = ""
            while i < len(palabras):
                tentativa = (linea + " " + palabras[i]).strip()
                if len(tentativa) > cupo:
                    break
                linea, i = tentativa, i + 1
            if relleno:
                # el guion es mucho mas angosto que la letra media, asi que el
                # relleno se calcula por ancho y no contando caracteres
                usado = len(linea) * char_mm + (char_mm if linea else 0)
                cabe = int(max(ancho - usado, 0) / (cuerpo * 0.12))
                if cabe > 0:
                    linea = (linea + " " if linea else "") + relleno * cabe
            filas.append((x, y, ancho, linea))
        if i < len(palabras):
            raise UserError(_(
                "El monto en palabras no cabe en los dos renglones del cheque: %s",
                self._vsg_amount_in_words()))
        return filas

    def _vsg_char_mm(self):
        """Ancho medio de caracter en mm, medido contra la salida real.

        En Arial las mayusculas ocupan bastante mas que la minuscula, y el
        monto se imprime en mayusculas en casi todos los formularios.
        """
        self.ensure_one()
        journal = self._vsg_journal()
        font = journal.vsg_check_font_size or 11.0
        return font * (0.225 if journal.vsg_check_uppercase else 0.19)

    def _vsg_place_font(self):
        """Cuerpo de letra de la ciudad, reducido para no invadir la fecha.

        La ciudad se imprime a la izquierda de las casillas de la fecha; un
        nombre largo como "Vina del Mar" chocaria con el primer digito del dia.
        """
        self.ensure_one()
        journal = self._vsg_journal()
        base = journal.vsg_check_font_size or 11.0
        texto = journal.vsg_check_place or ""
        if not texto:
            return base
        limite = None
        if journal.vsg_check_cells:
            try:
                primera = float((journal.vsg_check_date_cells or "").split(",")[0])
                # 4 mm de resguardo: la casilla se declara por su centro y el
                # digito ocupa algo mas de un milimetro hacia la izquierda
                limite = primera - 4.0 - journal.vsg_check_place_x
            except (ValueError, IndexError):
                limite = None
        if not limite or limite <= 0:
            return base
        necesario = base * limite / (len(texto) * self._vsg_char_mm())
        return round(max(min(base, necesario), base * 0.6), 1)

    def _vsg_words_font(self):
        """Cuerpo de letra del monto en palabras, reducido si no cabe en una linea.

        En un cheque una sola linea se lee mejor que dos, de modo que primero
        se achica la letra y solo despues se parte el texto.
        """
        self.ensure_one()
        journal = self._vsg_journal()
        base = journal.vsg_check_font_size or 11.0
        ancho = journal.vsg_check_words_width or 140.0
        largo = len(self._vsg_amount_in_words())
        if not largo:
            return base
        necesario = base * ancho / (largo * self._vsg_char_mm())
        return round(max(min(base, necesario), base * 0.65), 1)

    def _vsg_date_parts(self):
        """Dia, mes y anio de la fecha del cheque."""
        self.ensure_one()
        journal = self._vsg_journal()
        date = self.payment_date or self.payment_id.date or fields.Date.context_today(self)
        month = MONTHS_ES[date.month - 1] if journal.vsg_check_month_name else "%02d" % date.month
        return {
            "day": "%02d" % date.day,
            "numeric_month": "%02d" % date.month,
            "month": month,
            "year": "%04d" % date.year,
            "full": "%02d de %s de %04d" % (date.day, MONTHS_ES[date.month - 1], date.year)
            if journal.vsg_check_month_name
            else "%02d/%02d/%04d" % (date.day, date.month, date.year),
        }

    def _vsg_payee(self):
        self.ensure_one()
        partner = self.partner_id or self.payment_id.partner_id
        return partner.name or ""

    def _vsg_text(self, value):
        """Aplica mayusculas cuando el diario lo pide."""
        self.ensure_one()
        value = value or ""
        return value.upper() if self._vsg_journal().vsg_check_uppercase else value

    def _vsg_check_printable(self):
        """Valida que el cheque se pueda imprimir y devuelve los imprimibles."""
        printable = self.env["l10n_latam.check"]
        for check in self:
            journal = check._vsg_journal()
            if check.payment_method_code != "own_checks":
                raise UserError(_(
                    "El cheque %s no es un cheque propio; solo se imprimen cheques propios.",
                    check.display_name,
                ))
            if not journal.vsg_check_printing:
                raise UserError(_(
                    "El diario %s no tiene habilitada la impresion de cheques. "
                    "Actívala en Contabilidad / Configuracion / Diarios, pestania Cheques.",
                    journal.display_name,
                ))
            printable |= check
        return printable

    def action_vsg_print_check(self):
        checks = self._vsg_check_printable()
        return self.env.ref(
            "ecm_check_printing.action_report_vsg_check"
        ).report_action(checks)

    def action_vsg_print_calibration(self):
        """Imprime la grilla milimetrada sobre el formulario del banco."""
        journals = self.mapped("payment_id.journal_id")
        return self.env.ref(
            "ecm_check_printing.action_report_vsg_check_calibration"
        ).report_action(journals)
