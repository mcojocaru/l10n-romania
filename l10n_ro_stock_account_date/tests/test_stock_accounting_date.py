# Copyright (C) 2020 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from odoo.addons.l10n_ro_stock_account.tests.common import TestStockCommon

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestStockReport(TestStockCommon):
    def set_stock(self, product, qty):
        inventory_obj = self.env["stock.quant"].with_context(inventory_mode=True)
        inventory = inventory_obj.create(
            {
                "location_id": self.location_warehouse.id,
                "product_id": product.id,
                "inventory_quantity": qty,
            }
        )
        inventory._apply_inventory()

    def trasfer(self, location, location_dest, product=None, accounting_date=False):

        self.PickingObj = self.env["stock.picking"]
        self.MoveObj = self.env["stock.move"]
        self.MoveObj = self.env["stock.move"]

        if not product:
            product = self.product_mp

        picking = self.PickingObj.create(
            {
                "picking_type_id": self.picking_type_transfer.id,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
            }
        )
        self.MoveObj.create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": 2,
                "product_uom": product.uom_id.id,
                "picking_id": picking.id,
                "location_id": location.id,
                "location_dest_id": location_dest.id,
            }
        )
        if accounting_date:
            picking.accounting_date = accounting_date
        picking.action_confirm()
        picking.action_assign()
        for move_line in picking.move_lines:
            if move_line.product_uom_qty > 0 and move_line.quantity_done == 0:
                move_line.write({"quantity_done": move_line.product_uom_qty})
        picking._action_done()
        return picking

    def test_inventory(self):
        self.make_puchase()
        acc_date = fields.Date.today() - timedelta(days=1)
        inventory_obj = self.env["stock.quant"].with_context(inventory_mode=True)
        inventory = inventory_obj.create(
            {
                "location_id": self.location_warehouse.id,
                "product_id": self.product_1.id,
                "inventory_quantity": self.qty_po_p1 + 10,
            }
        )
        inventory.accounting_date = acc_date
        inventory._apply_inventory()
        stock_move = self.env["stock.move"].search(
            [
                (
                    "location_id",
                    "=",
                    inventory.product_id.with_company(
                        inventory.company_id
                    ).property_stock_inventory.id,
                )
            ]
        )

        self.assertEqual(stock_move.date.date(), acc_date)
        self.assertEqual(stock_move.move_line_ids.date.date(), acc_date)
        self.assertEqual(
            stock_move.stock_valuation_layer_ids.create_date.date(), acc_date
        )
        self.assertEqual(stock_move.account_move_ids.date, acc_date)

    def test_transfer(self):
        self.set_stock(self.product_mp, 1000)
        acc_date = fields.Date.today() - timedelta(days=1)
        location_id = self.picking_type_transfer.default_location_src_id
        location_dest_id = self.picking_type_transfer.default_location_dest_id.copy(
            {"l10n_ro_property_stock_valuation_account_id": self.account_valuation.id}
        )
        _logger.info("Start transfer")
        picking = self.trasfer(location_id, location_dest_id, accounting_date=acc_date)
        stock_move = picking.move_lines
        _logger.info("Tranfer efectuat")
        self.assertEqual(picking.accounting_date.date(), acc_date)
        self.assertEqual(stock_move.date.date(), acc_date)
        self.assertEqual(stock_move.move_line_ids.date.date(), acc_date)
        self.assertEqual(
            stock_move.stock_valuation_layer_ids.mapped("create_date")[0].date(),
            acc_date,
        )
        self.assertEqual(stock_move.account_move_ids.date, acc_date)
