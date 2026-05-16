from urllib import error, request

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .lead_payload import parse_payload


class RealEstateLeadSource(models.Model):
    _name = "real.estate.lead.source"
    _description = "Real Estate Lead Source"
    _order = "sequence, name"
    _check_company_auto = True

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    source_type = fields.Selection(
        [
            ("meta", "Meta Lead Ads"),
            ("marketplace", "Marketplace Feed"),
            ("website_xml", "Website XML Feed"),
        ],
        required=True,
        default="meta",
    )
    payload_format = fields.Selection(
        [("json", "JSON"), ("xml", "XML")], required=True, default="json"
    )
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible Realtor",
        domain="[('share', '=', False)]",
        default=lambda self: self.env.user,
    )
    team_id = fields.Many2one("crm.team", string="Sales Team", check_company=True)
    priority_score = fields.Integer(default=10, help="Base score added to every lead from this source.")
    score_phone = fields.Integer(default=20, string="Phone Score")
    score_email = fields.Integer(default=15, string="Email Score")
    budget_high_threshold = fields.Monetary(default=200000, currency_field="company_currency_id")
    budget_medium_threshold = fields.Monetary(default=100000, currency_field="company_currency_id")
    score_budget_high = fields.Integer(default=30, string="High Budget Score")
    score_budget_medium = fields.Integer(default=20, string="Medium Budget Score")
    score_budget_low = fields.Integer(default=10, string="Any Budget Score")
    score_urgent = fields.Integer(default=20, string="Urgent Message Score")
    score_max = fields.Integer(default=100, string="Maximum Score")
    urgent_keywords = fields.Char(default="urgent,today,asap")
    high_budget_threshold = fields.Monetary(default=150000, currency_field="company_currency_id")
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    api_url = fields.Char(string="API URL", groups="sales_team.group_sale_manager")
    api_token = fields.Char(string="API Token", groups="sales_team.group_sale_manager")
    api_auth_header = fields.Char(
        string="API Token Header",
        default="Authorization",
        groups="sales_team.group_sale_manager",
    )
    api_auth_prefix = fields.Char(
        string="API Token Prefix",
        default="Bearer",
        groups="sales_team.group_sale_manager",
    )
    api_timeout = fields.Integer(default=15, groups="sales_team.group_sale_manager")
    test_payload = fields.Text(string="Test Payload", groups="sales_team.group_sale_manager")
    utm_source_id = fields.Many2one("utm.source", string="CRM Source", readonly=True)
    last_import_date = fields.Datetime(readonly=True)
    last_error = fields.Text(readonly=True)
    lead_ids = fields.One2many("real.estate.lead.inbox", "source_id", string="Leads")
    lead_count = fields.Integer(compute="_compute_counts")
    duplicate_count = fields.Integer(compute="_compute_counts")
    converted_count = fields.Integer(compute="_compute_counts")
    failed_count = fields.Integer(compute="_compute_counts")

    @api.constrains(
        "api_timeout",
        "score_max",
        "budget_high_threshold",
        "budget_medium_threshold",
        "high_budget_threshold",
    )
    def _check_positive_settings(self):
        for source in self:
            if source.api_timeout <= 0:
                raise ValidationError(_("API timeout must be greater than zero."))
            if source.score_max <= 0:
                raise ValidationError(_("Maximum score must be greater than zero."))
            if source.budget_high_threshold < source.budget_medium_threshold:
                raise ValidationError(_("High budget threshold must be greater than medium threshold."))
            if source.high_budget_threshold < 0:
                raise ValidationError(_("High budget filter threshold cannot be negative."))

    @api.depends("lead_ids.status")
    def _compute_counts(self):
        grouped = self.env["real.estate.lead.inbox"]._read_group(
            [("source_id", "in", self.ids)], ["source_id", "status"], ["__count"]
        )
        counts = {}
        for source, status, count in grouped:
            source_counts = counts.setdefault(source.id, {"total": 0})
            source_counts["total"] += count
            source_counts[status] = count
        for source in self:
            source_counts = counts.get(source.id, {})
            source.lead_count = source_counts.get("total", 0)
            source.duplicate_count = source_counts.get("duplicate", 0)
            source.converted_count = source_counts.get("converted", 0)
            source.failed_count = source_counts.get("failed", 0)

    def action_import_leads(self):
        for source in self:
            source._import_leads()
        return True

    def _import_leads(self):
        self.ensure_one()
        self._ensure_utm_source()
        try:
            payload = self._get_payload()
            parsed_leads = parse_payload(self.source_type, self.payload_format, payload)
        except Exception as exc:
            self.write({"last_import_date": fields.Datetime.now(), "last_error": str(exc)})
            raise UserError(_("Lead import failed: %s") % exc) from exc
        inbox_model = self.env["real.estate.lead.inbox"]
        errors = []
        for values in parsed_leads:
            try:
                inbox_model.create_from_import(self, values)
            except Exception as exc:
                errors.append(str(exc))
        self.write(
            {
                "last_import_date": fields.Datetime.now(),
                "last_error": "\n".join(errors),
            }
        )
        return True

    def _get_payload(self):
        self.ensure_one()
        if self.api_url:
            headers = self._api_headers()
            api_request = request.Request(self.api_url, headers=headers, method="GET")
            try:
                with request.urlopen(api_request, timeout=self.api_timeout) as response:
                    return response.read().decode("utf-8")
            except error.URLError as exc:
                raise UserError(_("Could not fetch leads from %s: %s") % (self.api_url, exc)) from exc
        if self.test_payload:
            return self.test_payload
        raise UserError(_("Add an API URL or a test payload before importing leads."))

    def _api_headers(self):
        self.ensure_one()
        if not self.api_token or not self.api_auth_header:
            return {}
        token = self.api_token.strip()
        prefix = (self.api_auth_prefix or "").strip()
        return {self.api_auth_header.strip(): "%s %s" % (prefix, token) if prefix else token}

    def _score_options(self):
        self.ensure_one()
        return {
            "source_priority": self.priority_score,
            "phone_score": self.score_phone,
            "email_score": self.score_email,
            "budget_high_threshold": self.budget_high_threshold,
            "budget_medium_threshold": self.budget_medium_threshold,
            "budget_high_score": self.score_budget_high,
            "budget_medium_score": self.score_budget_medium,
            "budget_low_score": self.score_budget_low,
            "urgent_score": self.score_urgent,
            "urgent_keywords": [word.strip() for word in (self.urgent_keywords or "").split(",")],
            "max_score": self.score_max,
        }

    def _ensure_utm_source(self):
        self.ensure_one()
        if self.utm_source_id:
            return self.utm_source_id
        utm_source = self.env["utm.source"].search([("name", "=", self.name)], limit=1)
        if not utm_source:
            utm_source = self.env["utm.source"].create({"name": self.name})
        self.utm_source_id = utm_source
        return utm_source