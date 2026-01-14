# import frappe
# from frappe.utils import today, getdate

# @frappe.whitelist()
# def get_meal_pricing(participant_type):
#     print("\n\n\nget_meal_pricing\n\n\n\n")
#     MEAL_ITEM = "Meal Coupon"
#     today_date = getdate(today())

#     # 1. Check Pricing Rule exists
#     pricing_rule = frappe.db.exists(
#         "Pricing Rule",
#         {
#             "apply_on": "Item Code",
#             "item_code": MEAL_ITEM,
#             "for_item_code": participant_type,
#             "selling": 1,
#             "disabled": 0
#         }
#     )

#     if not pricing_rule:
#         return {
#             "has_meal": 0
#         }

#     # 2. Get valid Item Price
#     item_price = frappe.db.sql("""
#         SELECT
#             name,
#             price_list_rate,
#             valid_from,
#             valid_upto,
#             note
#         FROM `tabItem Price`
#         WHERE
#             item_code = %s
#             AND selling = 1
#             AND (%s BETWEEN IFNULL(valid_from, '2000-01-01')
#                         AND IFNULL(valid_upto, '2099-12-31'))
#         ORDER BY valid_from DESC
#         LIMIT 1
#     """, (MEAL_ITEM, today_date), as_dict=True)

#     if not item_price:
#         return {
#             "has_meal": 1,
#             "price": 0,
#             "note": "Price not configured"
#         }

#     return {
#         "has_meal": 1,
#         "price": item_price[0].price_list_rate,
#         "note": item_price[0].note or "",
#         "valid_from": item_price[0].valid_from,
#         "valid_upto": item_price[0].valid_upto,
#         "item_description": frappe.db.get_value("Item", participant_type, "description")
#     }

import frappe

@frappe.whitelist(allow_guest=True)
def test_participant_type(item_name, item_code):
    frappe.log_error(
        title="WEB FORM API HIT",
        message=f"Item Name: {item_name}\nItem Code: {item_code}"
    )

    print("API CALLED ✅")
    print(item_name, item_code)

    return {
        "status": "success",
        "item_name": item_name,
        "item_code": item_code
    }
