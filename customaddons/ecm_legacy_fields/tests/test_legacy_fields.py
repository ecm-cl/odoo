from odoo.tests.common import TransactionCase
from lxml import etree


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

    def test_field_labels_group_exports_by_origin_and_migration(self):
        move_fields = self.env["account.move"]._fields
        line_fields = self.env["account.move.line"]._fields

        self.assertEqual(move_fields["x_legacy_batch_id"].string, "Migración: Lote")
        self.assertEqual(
            move_fields["x_legacy_key"].string,
            "Migración: ID",
        )
        self.assertEqual(
            move_fields["x_legacy_numero"].string,
            "Origen: Número de comprobante (NUMERO)",
        )
        self.assertEqual(
            move_fields["x_legacy_tip_comp"].string,
            "Origen: Tipo de comprobante (TIP_COMP)",
        )
        self.assertEqual(
            move_fields["x_legacy_ano_mov"].string,
            "Origen: Año de movimiento (ANO_MOV)",
        )
        self.assertEqual(
            line_fields["x_legacy_linea"].string,
            "Origen: Número de línea (LINEA)",
        )
        self.assertEqual(
            line_fields["x_legacy_cta_item"].string,
            "Origen: CTA ítem (CTA_ITEM)",
        )
        self.assertEqual(
            line_fields["x_legacy_debe_ad"].string,
            "Origen: Debe adicional (DEBE_AD)",
        )
        self.assertEqual(
            line_fields["x_legacy_haber_ad"].string,
            "Origen: Haber adicional (HABER_AD)",
        )

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

    def test_list_labels_and_default_optional_columns(self):
        move_arch = self.env["account.move"].get_view(
            view_id=self.env.ref("account.view_move_tree").id,
            view_type="list",
        )["arch"]
        move_root = etree.fromstring(move_arch)
        move_defaults = {
            "x_legacy_batch_id": "Migración: Lote",
            "x_legacy_key": "Migración: ID",
            "x_legacy_numero": "Origen: Número de comprobante (NUMERO)",
            "x_legacy_tip_comp": "Origen: Tipo de comprobante (TIP_COMP)",
            "x_legacy_ano_mov": "Origen: Año de movimiento (ANO_MOV)",
        }
        for field_name, label in move_defaults.items():
            node = move_root.xpath(f".//field[@name='{field_name}']")[0]
            self.assertEqual(node.get("string"), label)
            self.assertEqual(node.get("optional"), "show")
        self.assertEqual(
            move_root.xpath(".//field[@name='partner_id' and @optional]")[0].get("optional"),
            "hide",
        )
        for field_name in {"ref", "company_id"}:
            node = move_root.xpath(f".//field[@name='{field_name}' and @optional]")[0]
            self.assertEqual(node.get("optional"), "show")

        line_arch = self.env["account.move.line"].get_view(
            view_id=self.env.ref("account.view_move_line_tree").id,
            view_type="list",
        )["arch"]
        line_root = etree.fromstring(line_arch)
        shown_legacy_fields = {
            "x_legacy_centro",
            "x_legacy_tip_docu",
            "x_legacy_num_docu",
            "x_legacy_tip_glosa",
            "x_legacy_tip_tabla",
            "x_legacy_tip_bim",
            "x_legacy_af_flujo",
            "x_legacy_nombre",
        }
        for field_name in shown_legacy_fields:
            node = line_root.xpath(f".//field[@name='{field_name}']")[0]
            self.assertEqual(node.get("optional"), "show")
            self.assertEqual(node.get("string"), self.env["account.move.line"]._fields[field_name].string)

        for field_name in {
            "invoice_date",
            "company_id",
            "journal_id",
            "partner_id",
            "ref",
            "name",
            "date_maturity",
            "balance",
        }:
            nodes = line_root.xpath(f".//field[@name='{field_name}' and @optional]")
            self.assertTrue(nodes)
            self.assertEqual(nodes[0].get("optional"), "show")

        matching_number = line_root.xpath(".//field[@name='matching_number' and @optional]")[0]
        self.assertEqual(matching_number.get("optional"), "hide")
