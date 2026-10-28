from odoo.tests.common import TransactionCase


class TestLegacyFields(TransactionCase):
    def test_legacy_fields_are_registered(self):
        move_fields = self.env["account.move"]._fields
        line_fields = self.env["account.move.line"]._fields
        batch_fields = self.env["account.legacy.import.batch"]._fields

        expected_move_fields = {
            "x_legacy_batch_id",
            "x_legacy_key",
            "x_legacy_numero",
            "x_legacy_tip_comp",
            "x_legacy_ano_mov",
        }
        expected_line_fields = {
            "x_legacy_linea",
            "x_legacy_cuenta",
            "x_legacy_cta_item",
            "x_legacy_dig_ver",
            "x_legacy_vencimiento",
            "x_legacy_centro",
            "x_legacy_tip_anal",
            "x_legacy_tip_docu",
            "x_legacy_num_docu",
            "x_legacy_tip_glosa",
            "x_legacy_ano",
            "x_legacy_tip_tabla",
            "x_legacy_num_adic",
            "x_legacy_cod_mon",
            "x_legacy_paridad",
            "x_legacy_bimfol",
            "x_legacy_tip_bim",
            "x_legacy_cambio",
            "x_legacy_af_flujo",
            "x_legacy_debe_ad",
            "x_legacy_haber_ad",
            "x_legacy_descrip",
            "x_legacy_nombre",
        }

        self.assertFalse(expected_move_fields - move_fields.keys())
        self.assertFalse(expected_line_fields - line_fields.keys())
        self.assertFalse(
            {
                "source_filename",
                "source_sheet",
                "source_sha256",
                "source_size",
                "source_move_count",
                "source_line_count",
                "source_debit_total",
                "source_credit_total",
            }
            - batch_fields.keys()
        )

    def test_legacy_field_labels_match_source_columns(self):
        move_fields = self.env["account.move"]._fields
        line_fields = self.env["account.move.line"]._fields

        self.assertEqual(move_fields["x_legacy_key"].string, "Identificador de asiento migrado")
        self.assertEqual(move_fields["x_legacy_numero"].string, "NUMERO")
        self.assertEqual(move_fields["x_legacy_tip_comp"].string, "TIP_COMP")
        self.assertEqual(move_fields["x_legacy_ano_mov"].string, "ANO_MOV")
        self.assertEqual(line_fields["x_legacy_linea"].string, "LINEA")
        self.assertEqual(line_fields["x_legacy_cta_item"].string, "CTA_ITEM")
        self.assertEqual(line_fields["x_legacy_debe_ad"].string, "DEBE_AD")
        self.assertEqual(line_fields["x_legacy_haber_ad"].string, "HABER_AD")

    def test_fields_preserve_legacy_values(self):
        batch = self.env["account.legacy.import.batch"].new(
            {
                "name": "VALSEGUR-2025-PILOTO-002",
                "company_id": self.env.company.id,
                "source_filename": "2025_Valsegur.xlsx",
                "source_sheet": "2025",
                "source_sha256": "a" * 64,
            }
        )
        move = self.env["account.move"].new(
            {
                "move_type": "entry",
                "x_legacy_batch_id": batch,
                "x_legacy_key": "valsegur_2025_T_1",
                "x_legacy_numero": "1",
                "x_legacy_tip_comp": "T",
                "x_legacy_ano_mov": 2025,
            }
        )
        line = self.env["account.move.line"].new(
            {
                "name": "Línea de prueba",
                "x_legacy_linea": 1,
                "x_legacy_cuenta": "1101001",
                "x_legacy_vencimiento": "01/01/1900",
                "x_legacy_nombre": "NOMBRE ORIGINAL",
            }
        )

        self.assertEqual(move.x_legacy_batch_id.name, "VALSEGUR-2025-PILOTO-002")
        self.assertEqual(move.x_legacy_key, "valsegur_2025_T_1")
        self.assertEqual(line.x_legacy_cuenta, "1101001")
        self.assertEqual(line.x_legacy_vencimiento, "01/01/1900")
        self.assertEqual(line.x_legacy_nombre, "NOMBRE ORIGINAL")
