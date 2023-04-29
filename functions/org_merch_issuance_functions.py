from database.org_db_funcs import OrgDataBase


def get_purchase_merch_fullname(db: OrgDataBase, purchase_id):
    name, stuff_id, stuff_sizes_colors_id, issued, count = db.execute("SELECT stuff.name, stuff.id, "
                                                                      "purchases.stuff_sizes_colors_id, "
                                                                      "purchases.issued, purchases.count "
                                                                      "FROM purchases "
                                                                      "JOIN stuff on purchases.stuff_id = stuff.id "
                                                                      "WHERE purchases.id = ?",
                                                                      purchase_id, fetch="one")
    size_color = db.get_stuff_sizes_colors(stuff_sizes_colors_id, "size, color")
    merch_fullname = name
    if size_color:
        size, color = size_color
        if size:
            merch_fullname += f" {size} "
        if color:
            merch_fullname += f" {color} "
    return merch_fullname
