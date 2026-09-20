@router.get("/{customer_id}")
def get_recommendations(
    customer_id: int,
    db: Session = Depends(get_db)
):
    previous_orders = (
        db.query(OrderItem)
        .join(
            Order,
            Order.order_id == OrderItem.order_id
        )
        .filter(
            Order.customer_id == customer_id
        )
        .all()
    )

    if not previous_orders:
        return []

    ordered_menu_ids = list(set(
        item.menu_id
        for item in previous_orders
    ))

    previous_menus = (
        db.query(Menu)
        .filter(
            Menu.menu_id.in_(ordered_menu_ids)
        )
        .all()
    )

    if not previous_menus:
        return []

    result = []

    for menu in previous_menus:

        result.append({
            "menu_id": menu.menu_id,
            "food_name": menu.food_name,
            "price": menu.price,
            "category": menu.category,
            "restaurant_id": menu.restaurant_id,
            "score": 10
        })

    return result