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
    # 3. Active warehouses (checkbox selection)
    # ------------------------------------------------
    # context.active_warehouses = frappe.form_dict.getlist("warehouses")

    # ------------------------------------------------
    # 4. Items (published only)
    # ------------------------------------------------
    items = frappe.get_all(
        "Item",
        filters={"custom_publish": 1,"item_group":["!=", "Registration"]},
        fields=[
            "name",
            "item_name",
            "item_group"
        ],
        order_by="item_name"
    )

    item_codes = [i.name for i in items]

    # ------------------------------------------------
    # 5. Valid Item Prices
    # ------------------------------------------------
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

    price_map = {}
    for p in prices:
        if p.item_code not in price_map:
            price_map[p.item_code] = p.price_list_rate

    for item in items:
        item.standard_rate = price_map.get(item.name, 0)

    context.items = items

    # ------------------------------------------------
    # 6. Item Groups (published items only)
    # ------------------------------------------------
    item_groups = sorted(
        {item.item_group for item in items if item.item_group}
    )

    context.item_groups = [{"name": g} for g in item_groups]

    return context
