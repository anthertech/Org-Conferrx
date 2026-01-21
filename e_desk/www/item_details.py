import frappe
from frappe.utils import nowdate, now_datetime, get_datetime

def get_context(context):
    user = frappe.session.user
    today = nowdate()
    now = now_datetime()

    # ------------------------------------------------
    # 1. Get item code from URL
    # ------------------------------------------------
    item_code = frappe.form_dict.get("item")
    if not item_code:
        frappe.throw("Item not specified")

    # ------------------------------------------------
    # 2. Valid participants → warehouses
    # ------------------------------------------------
    participants = frappe.get_all(
        "Participant",
        filters={"user": user},
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

        if not conf or not conf.default_warehouse:
            continue

        if conf.registration_close_date:
            close_dt = get_datetime(conf.registration_close_date)
            if close_dt < now:
                continue

        warehouses.append({
            "warehouse": conf.default_warehouse,
            "event": p.event
        })

    context.warehouses = warehouses

    # ------------------------------------------------
    # 3. Active warehouse & event
    # ------------------------------------------------
    active_warehouse = frappe.form_dict.get("warehouse")
    active_event = frappe.form_dict.get("event")

    context.active_warehouse = active_warehouse
    context.active_event = active_event

    if not active_warehouse:
        return context

    # ------------------------------------------------
    # 4. Fetch SINGLE item
    # ------------------------------------------------
    item = frappe.db.sql("""
        SELECT
            i.name,
            i.item_name,
            i.item_group,
            i.description,
            i.has_serial_no,
            b.actual_qty
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON i.name = b.item_code
        WHERE
            b.warehouse = %s
            AND i.name = %s
            AND b.actual_qty > 0
            AND i.custom_publish = 1
            AND i.disabled = 0
            AND i.is_sales_item = 1
        LIMIT 1
    """, (active_warehouse, item_code), as_dict=True)


    if not item:
        frappe.throw("Item not available")

    item = item[0]

    # ------------------------------------------------
    # 5. Price
    # ------------------------------------------------
    price = frappe.get_all(
        "Item Price",
        filters=[
            ["item_code", "=", item.name],
            ["valid_from", "<=", today]
        ],
        or_filters=[
            ["valid_upto", ">=", today],
            ["valid_upto", "is", "not set"]
        ],
        fields=["price_list_rate"],
        order_by="valid_from desc",
        limit=1
    )

    item.standard_rate = price[0].price_list_rate if price else 0

    # ------------------------------------------------
    # 6. Serial numbers (slots)
    # ------------------------------------------------
    item.serial_nos = []

    if item.has_serial_no:
        serials = frappe.get_all(
            "Serial No",
            filters={
                "item_code": item.name,
                "warehouse": active_warehouse,
                "status": "Active"
            },
            fields=["name","description"]
        )
        item.serial_nos = [s.name for s in serials]

    context.item = item
    print("\n\n\nitem",item)
    # ------------------------------------------------
    # 7. Conference currency
    # ------------------------------------------------
    context.currency = None
    if active_event:
        context.currency = frappe.get_value(
            "Conference",
            active_event,
            "currency"
        )

    return context
