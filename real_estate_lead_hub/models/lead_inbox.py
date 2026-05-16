from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Domain

from .lead_payload import lead_score, normalize_email, normalize_phone, to_float


class RealEstateLeadInbox(models.Model):
    _name = "real.estate.lead.inbox"
    _description = "Real Estate Lead Inbox"
    _order = "create_date desc, score desc"
    _check_company_auto = True

    name = fields.Char(required=True, default="New Real Estate Lead")
    source_id = fields.Many2one(
        "real.estate.lead.source", required=True, ondelete="cascade", check_company=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    external_id = fields.Char(index=True)
    contact_name = fields.Char(required=True)
    phone = fields.Char()
    phone_normalized = fields.Char(compute="_compute_normalized_contact", store=True, index=True)
    email = fields.Char()
    email_normalized = fields.Char(compute="_compute_normalized_contact", store=True, index=True)
    city = fields.Char()
    district = fields.Char()
    property_type = fields.Char()
    budget = fields.Monetary(currency_field="company_currency_id")
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    message = fields.Text()
    raw_payload = fields.Text(
        groups="sales_team.group_sale_manager",
        help="Original source payload for troubleshooting. Keep retention short if feeds contain sensitive client data.",
    )
    user_id = fields.Many2one("res.users", string="Responsible Realtor")
    team_id = fields.Many2one("crm.team", string="Sales Team", check_company=True)
    status = fields.Selection(
        [
            ("new", "New"),
            ("duplicate", "Duplicate"),
            ("converted", "Converted"),
            ("skipped", "Skipped"),
            ("failed", "Failed"),
        ],
        required=True,
        default="new",
        index=True,
    )
    score = fields.Integer(compute="_compute_score", store=True, index=True)
    is_high_budget = fields.Boolean(compute="_compute_is_high_budget", store=True, index=True)
    is_high_score = fields.Boolean(compute="_compute_is_high_score", store=True, index=True)
    duplicate_inbox_id = fields.Many2one("real.estate.lead.inbox", readonly=True)
    existing_lead_id = fields.Many2one("crm.lead", readonly=True)
    opportunity_id = fields.Many2one("crm.lead", readonly=True)
    converted_date = fields.Datetime(readonly=True)
    import_date = fields.Datetime(default=fields.Datetime.now, readonly=True)

    @api.depends("phone", "email")
    def _compute_normalized_contact(self):
        for lead in self:
            lead.phone_normalized = normalize_phone(lead.phone)
            lead.email_normalized = normalize_email(lead.email)

    @api.depends(
        "budget",
        "phone",
        "email",
        "message",
        "source_id.priority_score",
        "source_id.score_phone",
        "source_id.score_email",
        "source_id.budget_high_threshold",
        "source_id.budget_medium_threshold",
        "source_id.score_budget_high",
        "source_id.score_budget_medium",
        "source_id.score_budget_low",
        "source_id.score_urgent",
        "source_id.urgent_keywords",
        "source_id.score_max",
    )
    def _compute_score(self):
        for lead in self:
            lead.score = lead_score(
                {
                    "budget": lead.budget,
                    "phone": lead.phone,
                    "email": lead.email,
                    "message": lead.message,
                },
                lead.source_id._score_options(),
            )

    @api.depends("budget", "source_id.high_budget_threshold")
    def _compute_is_high_budget(self):
        for lead in self:
            lead.is_high_budget = bool(
                lead.source_id.high_budget_threshold
                and lead.budget >= lead.source_id.high_budget_threshold
            )

    @api.depends("score", "source_id.score_max")
    def _compute_is_high_score(self):
        for lead in self:
            lead.is_high_score = bool(
                lead.source_id.score_max
                and lead.score >= lead.source_id.score_max * 0.7
            )

    @api.model
    def create_from_import(self, source, values):
        contact_name = values.get("contact_name") or _("Unknown Client")
        vals = {
            "name": _("%s from %s") % (contact_name, source.name),
            "source_id": source.id,
            "company_id": source.company_id.id,
            "external_id": values.get("external_id"),
            "contact_name": contact_name,
            "phone": values.get("phone"),
            "email": values.get("email"),
            "city": values.get("city"),
            "district": values.get("district"),
            "property_type": values.get("property_type"),
            "budget": to_float(values.get("budget")),
            "message": values.get("message"),
            "raw_payload": values.get("raw_payload"),
            "user_id": source.user_id.id,
            "team_id": source.team_id.id,
        }
        duplicate_inbox = self._find_duplicate_inbox(source, vals)
        existing_lead = self._find_existing_lead(vals)
        if duplicate_inbox or existing_lead:
            vals["status"] = "duplicate"
            vals["duplicate_inbox_id"] = duplicate_inbox.id if duplicate_inbox else False
            vals["existing_lead_id"] = existing_lead.id if existing_lead else False
        return self.create(vals)

    def action_convert_to_opportunity(self):
        for lead in self:
            lead._convert_to_opportunity()
        return True

    def _convert_to_opportunity(self):
        self.ensure_one()
        if self.status == "converted" and self.opportunity_id:
            return self.opportunity_id
        if self.status == "duplicate":
            raise UserError(_("Review duplicate leads before creating a new opportunity."))
        utm_source = self.source_id._ensure_utm_source()
        opportunity = self.env["crm.lead"].create(
            {
                "name": self._opportunity_name(),
                "type": "opportunity",
                "contact_name": self.contact_name,
                "phone": self.phone,
                "email_from": self.email,
                "expected_revenue": self.budget,
                "description": self._opportunity_description(),
                "user_id": self.user_id.id,
                "team_id": self.team_id.id,
                "source_id": utm_source.id,
                "company_id": self.company_id.id,
            }
        )
        self.write(
            {
                "status": "converted",
                "opportunity_id": opportunity.id,
                "converted_date": fields.Datetime.now(),
            }
        )
        return opportunity

    def action_open_opportunity(self):
        self.ensure_one()
        if not self.opportunity_id:
            raise UserError(_("No opportunity has been created for this lead yet."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Opportunity"),
            "res_model": "crm.lead",
            "view_mode": "form",
            "res_id": self.opportunity_id.id,
        }

    def action_skip(self):
        self.write({"status": "skipped"})
        return True

    def _find_duplicate_inbox(self, source, vals):
        external_id = vals.get("external_id")
        if not external_id:
            return self.browse()
        return self.search(
            [("source_id", "=", source.id), ("external_id", "=", external_id)], limit=1
        )

    def _find_existing_lead(self, vals):
        domains = []
        email = normalize_email(vals.get("email"))
        phone = normalize_phone(vals.get("phone"))
        if email:
            domains.append([("email_normalized", "=", email)])
        if phone:
            if "phone_sanitized" in self.env["crm.lead"]._fields:
                domains.append([("phone_sanitized", "ilike", phone)])
            else:
                domains.append([("phone", "ilike", phone)])
        if not domains:
            return self.env["crm.lead"].browse()
        domain = Domain.OR(domains)
        return self.env["crm.lead"].search(domain, limit=1)

    def _opportunity_name(self):
        parts = [self.contact_name]
        if self.city:
            parts.append(self.city)
        if self.property_type:
            parts.append(self.property_type)
        return " - ".join(parts)

    def _opportunity_description(self):
        lines = [self.message or ""]
        details = [
            (_("City"), self.city),
            (_("District"), self.district),
            (_("Property Type"), self.property_type),
            (_("Budget"), self.budget),
            (_("Source"), self.source_id.name),
            (_("External Lead ID"), self.external_id),
            (_("Lead Score"), self.score),
        ]
        lines += ["%s: %s" % (label, value) for label, value in details if value]
        return "\n".join(lines)