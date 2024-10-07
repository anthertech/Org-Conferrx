import frappe

def address_link(doc,event):
    links=[]
    for i in doc.links:
        chruch=False
        hotel=False
        if i.link_doctype=="Church":
            church=frappe.get_value("Church",i.link_name,"church")
            for j in doc.links:
                if i.link_doctype=="Church" and i.link_name==church and chruch==False:
                    chruch= True
            if chruch==False:
                links.append({"link_doctype":"Church","link_name":church})
        if i.link_doctype=="Hotel":
            hotel=frappe.get_value("Hotel",i.link_name,"hotel")
            for j in doc.links:
                if i.link_doctype=="Hotel" and i.link_name==hotel and hotel==False:
                    hotel= True
            if hotel==False:
                links.append({"link_doctype":"Hotel","link_name":hotel})
    doc.update({
        "links":doc.links+links

    })