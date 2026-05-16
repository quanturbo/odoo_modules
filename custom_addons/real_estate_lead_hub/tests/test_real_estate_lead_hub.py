import json

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestRealEstateLeadHub(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_model = cls.env["real.estate.lead.source"]
        cls.inbox_model = cls.env["real.estate.lead.inbox"]

    def test_meta_json_import_and_duplicate_detection(self):
        payload = {
            "data": [
                {
                    "id": "meta-001",
                    "field_data": [
                        {"name": "full_name", "values": ["Anna Koval"]},
                        {"name": "phone_number", "values": ["+380 67 111 22 33"]},
                        {"name": "email", "values": ["Anna@example.com"]},
                        {"name": "city", "values": ["Kyiv"]},
                        {"name": "district", "values": ["Pechersk"]},
                        {"name": "property_type", "values": ["Apartment"]},
                        {"name": "budget", "values": ["180000"]},
                        {"name": "message", "values": ["Need a viewing today"]},
                    ],
                },
                {
                    "id": "meta-001",
                    "field_data": [
                        {"name": "full_name", "values": ["Anna Koval"]},
                        {"name": "phone_number", "values": ["+380 67 111 22 33"]},
                    ],
                },
            ]
        }
        source = self.source_model.create(
            {
                "name": "Meta Lead Ads",
                "source_type": "meta",
                "payload_format": "json",
                "priority_score": 20,
                "test_payload": json.dumps(payload),
            }
        )

        source.action_import_leads()

        leads = self.inbox_model.search([("source_id", "=", source.id)], order="id")
        self.assertEqual(len(leads), 2)
        self.assertEqual(leads[0].status, "new")
        self.assertEqual(leads[1].status, "duplicate")
        self.assertGreaterEqual(leads[0].score, 70)
        self.assertEqual(leads[0].phone_normalized, "380671112233")
        self.assertTrue(leads[0].is_high_budget)
        self.assertEqual(source.lead_count, 2)
        self.assertEqual(source.duplicate_count, 1)

    def test_marketplace_json_import_and_conversion(self):
        payload = {
            "leads": [
                {
                    "lead_id": "market-001",
                    "client": {
                        "name": "Dmytro Melnyk",
                        "phone": "+380 50 222 33 44",
                        "email": "dmytro@example.com",
                    },
                    "property": {
                        "city": "Kyiv",
                        "district": "Podil",
                        "type": "Townhouse",
                        "budget": 240000,
                    },
                    "message": "Looking for a family home",
                }
            ]
        }
        source = self.source_model.create(
            {
                "name": "Marketplace Feed",
                "source_type": "marketplace",
                "payload_format": "json",
                "priority_score": 15,
                "test_payload": json.dumps(payload),
            }
        )

        source.action_import_leads()
        lead = self.inbox_model.search([("source_id", "=", source.id)], limit=1)
        lead.action_convert_to_opportunity()

        self.assertEqual(lead.status, "converted")
        self.assertTrue(lead.opportunity_id)
        self.assertEqual(lead.opportunity_id.contact_name, "Dmytro Melnyk")
        self.assertEqual(lead.opportunity_id.expected_revenue, 240000)
        self.assertEqual(lead.opportunity_id.source_id.name, "Marketplace Feed")

    def test_website_xml_import(self):
        payload = """
            <leads>
                <lead>
                    <id>web-001</id>
                    <name>Olena Shevchenko</name>
                    <phone>+380 93 333 44 55</phone>
                    <email>olena@example.com</email>
                    <city>Kyiv</city>
                    <district>Obolon</district>
                    <property_type>Rental Apartment</property_type>
                    <budget>1200</budget>
                    <message>Need apartment ASAP</message>
                </lead>
            </leads>
        """
        source = self.source_model.create(
            {
                "name": "Website XML Feed",
                "source_type": "website_xml",
                "payload_format": "xml",
                "priority_score": 10,
                "test_payload": payload,
            }
        )

        source.action_import_leads()

        lead = self.inbox_model.search([("source_id", "=", source.id)], limit=1)
        self.assertEqual(lead.contact_name, "Olena Shevchenko")
        self.assertEqual(lead.city, "Kyiv")
        self.assertGreaterEqual(lead.score, 45)

    def test_source_configuration_controls_scoring_and_api_headers(self):
        source = self.source_model.create(
            {
                "name": "Partner API",
                "source_type": "marketplace",
                "payload_format": "json",
                "priority_score": 3,
                "score_phone": 4,
                "score_email": 5,
                "budget_high_threshold": 5000,
                "budget_medium_threshold": 1000,
                "score_budget_high": 30,
                "score_budget_medium": 12,
                "score_budget_low": 2,
                "score_urgent": 9,
                "urgent_keywords": "call now,priority",
                "score_max": 40,
                "high_budget_threshold": 4500,
                "api_token": "secret-token",
                "api_auth_header": "X-Lead-Token",
                "api_auth_prefix": "",
            }
        )

        lead = self.inbox_model.create_from_import(
            source,
            {
                "contact_name": "Configurable Client",
                "phone": "+380 44 000 11 22",
                "email": "config@example.com",
                "budget": 6000,
                "message": "Please call now",
            },
        )

        self.assertEqual(lead.score, 40)
        self.assertTrue(lead.is_high_budget)
        self.assertTrue(lead.is_high_score)
        self.assertEqual(source._api_headers(), {"X-Lead-Token": "secret-token"})

    def test_existing_crm_opportunity_marks_import_as_duplicate(self):
        existing = self.env["crm.lead"].create(
            {
                "name": "Existing Buyer",
                "type": "opportunity",
                "contact_name": "Existing Buyer",
                "phone": "+380501112233",
            }
        )
        source = self.source_model.create(
            {
                "name": "Phone Duplicate Source",
                "source_type": "marketplace",
                "payload_format": "json",
            }
        )

        lead = self.inbox_model.create_from_import(
            source,
            {
                "contact_name": "Existing Buyer Again",
                "phone": "+380 50 111 22 33",
            },
        )

        self.assertEqual(lead.status, "duplicate")
        self.assertEqual(lead.existing_lead_id, existing)

    def test_formatted_budget_values_are_normalized_on_import(self):
        payload = {
            "leads": [
                {
                    "lead_id": "formatted-budget-001",
                    "client": {"name": "Formatted Budget", "phone": "+380 67 000 11 22"},
                    "property": {"budget": "$1,234.56", "type": "Apartment"},
                }
            ]
        }
        source = self.source_model.create(
            {
                "name": "Formatted Budget Source",
                "source_type": "marketplace",
                "payload_format": "json",
                "budget_medium_threshold": 1000,
                "high_budget_threshold": 1200,
                "test_payload": json.dumps(payload),
            }
        )

        source.action_import_leads()

        lead = self.inbox_model.search([("external_id", "=", "formatted-budget-001")], limit=1)
        self.assertEqual(lead.budget, 1234.56)
        self.assertTrue(lead.is_high_budget)

    def test_meta_parser_ignores_unnamed_fields_and_short_phones(self):
        payload = {
            "data": [
                {
                    "id": "meta-defensive-001",
                    "field_data": [
                        {"values": ["ignored"]},
                        {"name": "full_name", "values": ["Defensive Lead"]},
                        {"name": "phone_number", "values": ["123"]},
                    ],
                }
            ]
        }
        source = self.source_model.create(
            {
                "name": "Meta Defensive Source",
                "source_type": "meta",
                "payload_format": "json",
                "test_payload": json.dumps(payload),
            }
        )

        source.action_import_leads()

        lead = self.inbox_model.search([("external_id", "=", "meta-defensive-001")], limit=1)
        self.assertEqual(lead.contact_name, "Defensive Lead")
        self.assertFalse(lead.phone_normalized)