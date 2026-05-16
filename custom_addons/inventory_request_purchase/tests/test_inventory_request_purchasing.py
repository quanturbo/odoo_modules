from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestInventoryRequestPurchasing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Inventory Request Test Product"}
        )

    def test_action_links_are_registered(self):
        for xmlid in (
            "inventory_request_purchase.action_stock_request_form",
            "inventory_request_purchase.view_stock_request_form",
            "purchase.purchase_rfq",
            "purchase.purchase_order_form",
            "purchase.purchase_order_tree",
        ):
            self.env.ref(xmlid)

        self.assertIn("purchase_ids", self.env["stock.request"]._fields)
        self.assertIn("purchase_line_ids", self.env["stock.request"]._fields)
        self.assertIn("stock_request_ids", self.env["purchase.order.line"]._fields)
        self.assertIn("stock_request_ids", self.env["purchase.order"]._fields)

        self.env["stock.request"].browse().action_view_purchase()
        self.env["purchase.order"].browse().action_view_stock_request()

    def test_order_priority_is_carried_to_request(self):
        order = self.env["stock.request.order"].create(
            {
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "expected_date": fields.Datetime.now(),
                "priority": "3",
                "internal_note": "Critical replenishment",
            }
        )
        request = self.env["stock.request"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 2.0,
            }
        )

        self.assertEqual(request.priority, "3")
        self.assertEqual(request.requested_by, order.requested_by)
        self.assertEqual(request.warehouse_id, order.warehouse_id)
        self.assertEqual(request.location_id, order.location_id)

    def test_explicit_request_priority_is_preserved(self):
        order = self.env["stock.request.order"].create(
            {
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "expected_date": fields.Datetime.now(),
                "priority": "3",
            }
        )
        request = self.env["stock.request"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "priority": "0",
            }
        )

        self.assertEqual(request.priority, "0")
