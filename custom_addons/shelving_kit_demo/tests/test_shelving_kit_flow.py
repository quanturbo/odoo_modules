from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestShelvingKitFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env.ref("shelving_kit_demo.vendor_rapid_home_goods")
        cls.parent_product = cls.env.ref("shelving_kit_demo.product_shelving_unit_48_18_84")
        cls.bom = cls.env.ref("shelving_kit_demo.bom_shelving_unit_48_18_84")
        cls.stock_location = cls.env.ref("stock.warehouse0").lot_stock_id
        cls.customer = cls.env["res.partner"].create({"name": "Shelving Kit Test Customer"})

    def _ensure_component_stock(self):
        for bom_line in self.bom.bom_line_ids:
            self.env["stock.quant"]._update_available_quantity(
                bom_line.product_id,
                self.stock_location,
                bom_line.product_qty * 2,
            )

    def test_supplier_discounted_cost_follows_list_price(self):
        seller = self.env.ref("shelving_kit_demo.seller_component_upright_post_84")

        self.assertEqual(seller.price, 120.00)
        self.assertEqual(seller.discount, 65.00)
        self.assertAlmostEqual(seller.price_discounted, 42.00)

        seller.price = 200.00

        self.assertAlmostEqual(seller.price_discounted, 70.00)

    def test_sale_order_for_parent_reserves_components(self):
        self._ensure_component_stock()

        sale_order = self.env["sale.order"].create({
            "partner_id": self.customer.id,
            "order_line": [(0, 0, {
                "product_id": self.parent_product.id,
                "product_uom_qty": 1.0,
            })],
        })

        sale_order.action_confirm()
        sale_order.picking_ids.action_assign()

        component_quantities = {
            line.product_id.id: line.product_qty
            for line in self.bom.bom_line_ids
        }
        delivery_moves = sale_order.picking_ids.move_ids.filtered(lambda move: move.product_id.id in component_quantities)

        self.assertFalse(sale_order.picking_ids.move_ids.filtered(lambda move: move.product_id == self.parent_product))
        self.assertEqual(set(delivery_moves.mapped("product_id").ids), set(component_quantities))
        for move in delivery_moves:
            self.assertEqual(move.product_uom_qty, component_quantities[move.product_id.id])
            self.assertEqual(move.quantity, component_quantities[move.product_id.id])
            self.assertEqual(move.state, "assigned")

    def test_purchase_order_for_reorder_component_is_receivable(self):
        component = self.env.ref("shelving_kit_demo.product_component_upright_post_84")
        seller = self.env.ref("shelving_kit_demo.seller_component_upright_post_84")
        orderpoint = self.env.ref("shelving_kit_demo.orderpoint_component_upright_post_84")
        quantity_before = component.qty_available
        existing_line_ids = self.env["purchase.order.line"].search([
            ("orderpoint_id", "=", orderpoint.id),
            ("product_id", "=", component.id),
        ]).ids

        orderpoint.qty_to_order = 1.0
        orderpoint.action_replenish()

        purchase_order_line = self.env["purchase.order.line"].search([
            ("id", "not in", existing_line_ids),
            ("orderpoint_id", "=", orderpoint.id),
            ("product_id", "=", component.id),
        ], order="id desc", limit=1)
        purchase_order = purchase_order_line.order_id

        self.assertTrue(purchase_order, "The reorder rule should generate a purchase order.")
        self.assertEqual(purchase_order.partner_id, self.vendor)
        self.assertEqual(purchase_order_line.product_qty, 1.0)
        self.assertEqual(purchase_order_line.price_unit, seller.price)
        self.assertEqual(purchase_order_line.discount, seller.discount)
        self.assertEqual(purchase_order_line.price_unit_discounted, seller.price_discounted)
        purchase_order.button_confirm()

        receipt = purchase_order.picking_ids
        self.assertEqual(purchase_order.state, "purchase")
        self.assertEqual(len(receipt), 1)
        self.assertEqual(receipt.picking_type_id.code, "incoming")
        self.assertEqual(receipt.move_ids.product_id, component)

        receipt.move_ids.quantity = 1.0
        receipt.button_validate()

        self.assertEqual(receipt.state, "done")
        self.assertEqual(component.qty_available, quantity_before + 1.0)

    def test_seeded_catalog_matches_scope(self):
        components = self.bom.bom_line_ids.product_id
        reorder_rules = self.env["stock.warehouse.orderpoint"].search([("product_id", "in", components.ids)])

        self.assertEqual(len(components), 12)
        self.assertTrue(all(components.mapped("is_storable")))
        self.assertFalse(self.parent_product.is_storable)
        self.assertEqual(self.parent_product.default_code, "FG/RHG/DHG")
        self.assertEqual(self.parent_product.description_sale, "48-18-84-FST-PERFOREE-CLOSE-10-10-10")
        self.assertEqual(self.bom.type, "phantom")
        self.assertGreaterEqual(len(reorder_rules), 3)

    def test_demo_transactions_are_visible(self):
        demo_sale_order = self.env.ref("shelving_kit_demo.demo_sale_order_shelving_unit")
        demo_delivery = self.env.ref("shelving_kit_demo.demo_delivery_shelving_unit")
        demo_purchase_order = self.env.ref("shelving_kit_demo.demo_purchase_order_upright_post_84")
        demo_receipt = self.env.ref("shelving_kit_demo.demo_receipt_upright_post_84")
        component = self.env.ref("shelving_kit_demo.product_component_upright_post_84")

        self.assertEqual(demo_sale_order.state, "sale")
        self.assertEqual(demo_delivery.picking_type_id.code, "outgoing")
        self.assertEqual(demo_purchase_order.state, "purchase")
        self.assertEqual(demo_purchase_order.partner_id, self.vendor)
        self.assertEqual(demo_receipt.picking_type_id.code, "incoming")
        self.assertEqual(demo_receipt.state, "assigned")
        self.assertEqual(demo_receipt.move_ids.product_id, component)

    def test_demo_navigation_actions_are_populated(self):
        expected_counts = {
            "action_shelving_demo_products": 13,
            "action_shelving_demo_bom": 1,
            "action_shelving_demo_bom_lines": 12,
            "action_shelving_demo_vendor_prices": 12,
            "action_shelving_demo_reordering_rules": 3,
            "action_shelving_demo_sale_orders": 1,
            "action_shelving_demo_purchase_orders": 1,
            "action_shelving_demo_receipts": 1,
            "action_shelving_demo_receipt_lines": 1,
            "action_shelving_demo_deliveries": 1,
            "action_shelving_demo_delivery_lines": 12,
        }
        for action_xmlid, expected_count in expected_counts.items():
            action = self.env.ref(f"shelving_kit_demo.{action_xmlid}")
            actual_count = self.env[action.res_model].search_count(eval(action.domain or "[]"))
            self.assertEqual(actual_count, expected_count, action_xmlid)