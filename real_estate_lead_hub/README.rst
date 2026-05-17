Real Estate Lead Hub
====================

Real Estate Lead Hub gives a real estate agency one review inbox for leads coming from Meta ads, marketplace feeds, and website forms before they enter CRM.

It reduces duplicate work, helps managers focus on better leads first, and keeps conversion into standard Odoo opportunities simple for the sales team. The first version stays intentionally small and readable, so new import channels and scoring rules are easier to maintain later.

Real Estate Lead Hub is a small Odoo CRM module for agencies that receive client
requests from Meta Lead Ads, real estate marketplaces, and website feeds.

What it demonstrates
--------------------

* Odoo CRM integration using standard CRM opportunities.
* JSON import for Meta Lead Ads style payloads.
* JSON import for marketplace style payloads.
* XML import for website or portal payloads.
* Duplicate detection by external ID, phone, and email.
* Configurable lead scoring from budget, contact completeness, source priority, and urgent words.
* Standard Odoo list, form, search, pivot, and graph views.
* Clear access rules for CRM users and CRM managers.

Setup
-----

1. Install the module on an Odoo database with CRM installed.
2. Open CRM > Real Estate Lead Hub > Lead Sources.
3. Create a source and choose the channel type and payload format.
4. Configure API header settings and timeout if the source uses a real endpoint.
5. Adjust score weights, budget thresholds, urgent keywords, and the high-budget threshold.
6. Add either an API URL with token or paste a local test payload.
7. Click Import Leads.
8. Review imported leads in CRM > Real Estate Lead Hub > Lead Inbox.

Validation checklist
--------------------

* Import a Meta-style JSON payload and confirm inbox lines are created.
* Import a marketplace JSON payload and confirm city, district, budget, and message are mapped.
* Import a website XML payload and confirm the same review flow works.
* Import a repeated external lead and confirm it is marked as duplicate.
* Import a lead that matches an existing CRM opportunity by normalized phone or email.
* Change source scoring settings and confirm scores update without code changes.
* Convert a new inbox line and confirm an opportunity is created with the original details.
* Open pivot or graph views to compare source quality.

Design notes
------------

This module intentionally avoids heavy connector frameworks, queues, and custom
dashboards. The goal is a reliable portfolio module that is easy to read,
install, test, and extend.