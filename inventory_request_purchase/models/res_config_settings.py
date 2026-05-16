# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_stock_request_order = fields.Boolean(
        implied_group="inventory_request_purchase.group_stock_request_order"
    )

    stock_request_check_available_first = fields.Boolean(
        related="company_id.stock_request_check_available_first", readonly=False
    )
    stock_request_allow_virtual_loc = fields.Boolean(
        related="company_id.stock_request_allow_virtual_loc", readonly=False
    )

    # Dependencies
    @api.onchange("stock_request_allow_virtual_loc")
    def _onchange_stock_request_allow_virtual_loc(self):
        if self.stock_request_allow_virtual_loc:
            self.group_stock_multi_locations = True

