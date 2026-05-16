# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

from .purchase_request_linking import open_inventory_requests


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    stock_request_ids = fields.Many2many(
        comodel_name="stock.request",
        string="Inventory Requests",
        compute="_compute_stock_request_ids",
    )
    stock_request_count = fields.Integer(
        "Inventory Request #", compute="_compute_stock_request_ids"
    )

    @api.depends("order_line", "order_line.stock_request_ids")
    def _compute_stock_request_ids(self):
        for rec in self:
            rec.stock_request_ids = rec.order_line.mapped("stock_request_ids")
            rec.stock_request_count = len(rec.stock_request_ids)

    def _linked_inventory_requests(self):
        return self.mapped("stock_request_ids")

    def action_view_stock_request(self):
        return open_inventory_requests(self, self._linked_inventory_requests())
