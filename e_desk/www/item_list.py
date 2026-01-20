import frappe
from frappe.utils import nowdate,now_datetime, get_datetime

def get_context(context):
    user = frappe.session.user
    today = nowdate()
    now = now_datetime()

    # ------------------------------------------------
    # 1. Valid participants (registered & NOT outdated)
    # ------------------------------------------------
    participants = frappe.get_all(
        "Participant",
        filters={
            "user": user
        },
        fields=["name", "event"],
        order_by="creation desc"
    )

    warehouses = []

    for p in participants:
        conf = frappe.get_value(
            "Conference",
            p.event,
            ["registration_close_date", "default_warehouse"],
            as_dict=True
        )

        # Event must be active
        if not conf or not conf.default_warehouse:
            continue

        if conf.registration_close_date:
            close_dt = get_datetime(conf.registration_close_date)

            # Event expired
            if close_dt < now:
                continue      
            warehouses.append({
                "warehouse": conf.default_warehouse,
                "event": p.event
            })

    context.warehouses = warehouses


    # ------------------------------------------------
    active_warehouse = frappe.form_dict.get("warehouse")
    active_event = frappe.form_dict.get("event")

    context.active_warehouse = active_warehouse
    context.active_event = active_event

    # ------------------------------------------------
    # 4. Items (published only)
    # ------------------------------------------------
    items = []

    if active_warehouse:
        items = frappe.db.sql("""
            SELECT
                i.name,
                i.item_name,
                i.item_group,
                i.has_serial_no,
                b.actual_qty
            FROM `tabBin` b
            INNER JOIN `tabItem` i ON i.name = b.item_code
            WHERE
                b.warehouse = %s
                AND b.actual_qty > 0
                AND i.custom_publish = 1
                AND i.item_group != 'Stall'
                AND i.disabled = 0
                AND i.is_sales_item = 1
            ORDER BY i.item_name
        """, active_warehouse, as_dict=True)

    item_codes = [i.name for i in items]

    # ------------------------------------------------
    # 5. Prices
    # ------------------------------------------------
    price_map = {}
    if item_codes:
        prices = frappe.get_all(
            "Item Price",
            filters=[
                ["item_code", "in", item_codes],
                ["valid_from", "<=", today]
            ],
            or_filters=[
                ["valid_upto", ">=", today],
                ["valid_upto", "is", "not set"]
            ],
            fields=["item_code", "price_list_rate", "valid_from"],
            order_by="valid_from desc"
        )

        for p in prices:
            if p.item_code not in price_map:
                price_map[p.item_code] = p.price_list_rate

    # ------------------------------------------------
    # 6. Serial numbers (slots)
    # ------------------------------------------------
    serial_map = {}
    serialized_items = [i.name for i in items if i.has_serial_no]

    if serialized_items:
        serials = frappe.get_all(
            "Serial No",
            filters={
                "item_code": ["in", serialized_items],
                "warehouse": active_warehouse,
                "status": "Available"
            },
            fields=["name", "item_code"]
        )

        for s in serials:
            serial_map.setdefault(s.item_code, []).append(s.name)

    # ------------------------------------------------
    # 7. Attach price + serials
    # ------------------------------------------------
    for item in items:
        item.standard_rate = price_map.get(item.name, 0)
        item.serial_nos = serial_map.get(item.name, [])

    context.items = items

    # ------------------------------------------------
    # 6. Item Groups (published items only)
    # ------------------------------------------------
    item_groups = sorted(
        {item.item_group for item in items if item.item_group}
    )

    context.item_groups = [{"name": g} for g in item_groups]
    # ------------------------------------------------
    # Company Currency
    # ------------------------------------------------
    default_company = frappe.defaults.get_user_default("Company") \
        or frappe.db.get_single_value("Global Defaults", "default_company")

    currency = frappe.get_value(
        "Company",
        default_company,
        "default_currency"
    )

    context.currency = currency


    return context
