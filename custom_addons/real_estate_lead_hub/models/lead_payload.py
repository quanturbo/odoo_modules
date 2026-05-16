import json
import re
from xml.etree import ElementTree


META_ALIASES = {
    "external_id": ("id", "lead_id", "external_id"),
    "contact_name": ("full_name", "contact_name", "name"),
    "phone": ("phone_number", "phone"),
    "email": ("email",),
    "city": ("city",),
    "district": ("district",),
    "property_type": ("property_type", "type"),
    "budget": ("budget",),
    "message": ("message", "comment"),
}

MARKETPLACE_ALIASES = {
    "external_id": ("lead_id", "external_id", "id"),
    "contact_name": ("contact_name", "client_name", "name"),
    "phone": ("phone", "client_phone"),
    "email": ("email", "client_email"),
    "city": ("city", "property_city"),
    "district": ("district", "property_district"),
    "property_type": ("property_type", "property_type_name"),
    "budget": ("budget", "property_budget"),
    "message": ("message", "comment"),
}

GENERIC_ALIASES = {
    "external_id": ("external_id", "id"),
    "contact_name": ("contact_name", "name"),
    "phone": ("phone",),
    "email": ("email",),
    "city": ("city",),
    "district": ("district",),
    "property_type": ("property_type",),
    "budget": ("budget",),
    "message": ("message",),
}


def normalize_email(email):
    return (email or "").strip().lower()


def normalize_phone(phone):
    digits = re.sub(r"\D+", "", phone or "")
    if digits.startswith("011"):
        digits = digits[3:]
    elif digits.startswith("00"):
        digits = digits[2:]
    return digits if len(digits) >= 7 else ""


def lead_score(values, score_options=None):
    options = score_options or {}
    score = int(options.get("source_priority") or 0)
    if normalize_phone(values.get("phone")):
        score += int(options.get("phone_score") or 0)
    if normalize_email(values.get("email")):
        score += int(options.get("email_score") or 0)
    budget = to_float(values.get("budget"))
    high_threshold = to_float(options.get("budget_high_threshold"))
    medium_threshold = to_float(options.get("budget_medium_threshold"))
    if high_threshold and budget >= high_threshold:
        score += int(options.get("budget_high_score") or 0)
    elif medium_threshold and budget >= medium_threshold:
        score += int(options.get("budget_medium_score") or 0)
    elif budget > 0:
        score += int(options.get("budget_low_score") or 0)
    message = (values.get("message") or "").lower()
    urgent_keywords = options.get("urgent_keywords") or []
    if any(keyword and keyword.lower() in message for keyword in urgent_keywords):
        score += int(options.get("urgent_score") or 0)
    return min(score, int(options.get("max_score") or score))


def parse_payload(source_type, payload_format, payload):
    if not payload:
        return []
    if payload_format == "xml":
        return _parse_xml_payload(payload)
    data = json.loads(payload)
    if source_type == "meta":
        return _parse_meta_json(data)
    if source_type == "marketplace":
        return _parse_marketplace_json(data)
    return _parse_generic_json(data)


def _parse_meta_json(data):
    leads = data.get("data") or data.get("leads") or []
    return [
        _mapped_json_lead(_meta_field_values(item), META_ALIASES, item)
        for item in leads
    ]


def _parse_marketplace_json(data):
    leads = data.get("leads") or data.get("items") or []
    return [
        _mapped_json_lead(_marketplace_field_values(item), MARKETPLACE_ALIASES, item)
        for item in leads
    ]


def _parse_generic_json(data):
    leads = data if isinstance(data, list) else data.get("leads", [])
    return [_mapped_json_lead(item, GENERIC_ALIASES, item) for item in leads]


def _parse_xml_payload(payload):
    root = ElementTree.fromstring(payload)
    parsed = []
    for lead in root.findall(".//lead"):
        item = {child.tag: (child.text or "").strip() for child in lead}
        parsed.append(
            _mapped_lead(
                item,
                GENERIC_ALIASES,
                ElementTree.tostring(lead, encoding="unicode"),
            )
        )
    return parsed


def _meta_field_values(item):
    values = {"id": item.get("id")}
    for field in item.get("field_data", []):
        field_name = field.get("name")
        if not field_name:
            continue
        field_values = field.get("values") or []
        values[field_name] = field_values[0] if field_values else ""
    return values


def _marketplace_field_values(item):
    values = dict(item)
    for prefix, nested in (
        ("client", item.get("client") or {}),
        ("property", item.get("property") or item.get("listing") or {}),
    ):
        values.update({"%s_%s" % (prefix, key): value for key, value in nested.items()})
    return values


def _mapped_json_lead(values, aliases, raw_item):
    return _mapped_lead(
        values,
        aliases,
        json.dumps(raw_item, ensure_ascii=False, indent=2),
    )


def _mapped_lead(values, aliases, raw_payload):
    result = {
        field_name: _first_value(values, names)
        for field_name, names in aliases.items()
    }
    result["raw_payload"] = raw_payload
    return result


def _first_value(values, names):
    for name in names:
        value = values.get(name)
        if value not in (None, False, ""):
            return value
    return False


def to_float(value):
    if value in (None, False, ""):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^0-9.,-]+", "", str(value))
    if "." in cleaned and "," in cleaned:
        decimal_separator = "." if cleaned.rfind(".") > cleaned.rfind(",") else ","
        thousands_separator = "," if decimal_separator == "." else "."
        cleaned = cleaned.replace(thousands_separator, "").replace(decimal_separator, ".")
    elif "," in cleaned:
        parts = cleaned.split(",")
        cleaned = "".join(parts) if len(parts[-1]) == 3 and len(parts) > 1 else cleaned.replace(",", ".")
    elif "." in cleaned:
        parts = cleaned.split(".")
        if len(parts[-1]) == 3 and len(parts) > 1:
            cleaned = "".join(parts)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0