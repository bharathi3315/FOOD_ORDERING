
import streamlit as st
import requests

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Food Ordering Platform",
    page_icon="🍔"
)

st.title("🍔 Food Ordering and Delivery Platform")

BASE_URL = "https://food-ordering-g7d5.onrender.com"


# ---------------- LOGIN ----------------

st.subheader("🔐 Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):

    if email and password:

        try:
            response = requests.post(
                f"{BASE_URL}/customers/login",
                params={
                    "email": email,
                    "password": password
                }
            )

            if response.status_code == 200:

                data = response.json()

                st.session_state["customer_id"] = data["customer_id"]
                st.session_state["customer_name"] = data["name"]
                st.session_state["customer_email"] = data["email"]

                st.success("Login successful!")
                st.write("Welcome,", data["name"])

            elif response.status_code == 401:

                st.error("Invalid email or password")

            else:

                st.error(
                    f"Login failed - Status Code: {response.status_code}"
                )

                st.code(response.text)

        except requests.exceptions.ConnectionError:

            st.error("Unable to connect to FastAPI backend")

    else:

        st.warning("Please enter Email and Password")


customer_id = st.session_state.get("customer_id")


# ---------------- FOOD MENU ----------------

st.subheader("🍴 Food Menu")

try:

    response = requests.get(
        f"{BASE_URL}/menus/"
    )

    if response.status_code == 200:

        menus = response.json()

        if menus:

            for item in menus:

                st.write("🍽️ Food:", item["food_name"])
                st.write("💰 Price:", item["price"])
                st.write("📂 Category:", item["category"])

                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    value=1,
                    key=f"qty_{item['menu_id']}"
                )

                if st.button(
                    "🛒 Order Now",
                    key=f"order_{item['menu_id']}"
                ):

                    if not customer_id:

                        st.warning("Please login first")

                    else:

                        order_response = requests.post(
                            f"{BASE_URL}/orders/",
                            params={
                                "customer_id": customer_id,
                                "restaurant_id": item["restaurant_id"],
                                "menu_id": item["menu_id"],
                                "quantity": quantity,
                                "total_amount": item["price"] * quantity
                            }
                        )

                        if order_response.status_code == 200:

                            order_data = order_response.json()

                            st.success(
                                "Order created successfully!"
                            )

                            st.write(
                                "Order ID:",
                                order_data["order_id"]
                            )

                        else:

                            st.error(
                                f"Unable to create order - "
                                f"Status Code: {order_response.status_code}"
                            )

                            st.code(order_response.text)

                st.divider()

        else:

            st.info("No food items available")

    else:

        st.error(
            f"Unable to load food menu - "
            f"Status Code: {response.status_code}"
        )

except requests.exceptions.ConnectionError:

    st.error("Unable to connect to FastAPI backend")


# ---------------- ORDER HISTORY ----------------

st.subheader("📜 My Order History")

if customer_id:

    try:

        history_response = requests.get(
            f"{BASE_URL}/orders/customer/{customer_id}/history"
        )

        if history_response.status_code == 200:

            history = history_response.json()

            if history:

                for order in history:

                    st.write(
                        "🧾 Order ID:",
                        order["order_id"]
                    )

                    st.write(
                        "🍽️ Food:",
                        order["food_name"]
                    )

                    st.write(
                        "🔢 Quantity:",
                        order["quantity"]
                    )

                    st.write(
                        "💰 Price:",
                        order["price"]
                    )

                    st.write(
                        "📌 Status:",
                        order["status"]
                    )

                    st.divider()

            else:

                st.info("No order history found")

        else:

            st.error(
                f"Unable to load order history - "
                f"Status Code: {history_response.status_code}"
            )

    except requests.exceptions.ConnectionError:

        st.error("Unable to connect to FastAPI backend")

else:

    st.info("Please login to view your order history")


# ---------------- RECOMMENDATIONS ----------------

st.subheader("⭐ Recommended For You")

if customer_id:

    try:

        recommendation_response = requests.get(
            f"{BASE_URL}/recommendations/{customer_id}"
        )

        if recommendation_response.status_code == 200:

            recommendations = recommendation_response.json()

            if recommendations:

                st.write(
                    "🍽️ Based on your previous orders:"
                )

                for item in recommendations:

                    st.write(
                        "🍴 Food:",
                        item["food_name"]
                    )

                    st.write(
                        "💰 Price:",
                        item["price"]
                    )

                    st.write(
                        "📂 Category:",
                        item["category"]
                    )

                    st.write(
                        "⭐ Recommendation Score:",
                        item["score"]
                    )

                    if st.button(
                        "🛒 Order Recommended Food",
                        key=f"recommend_{item['menu_id']}"
                    ):

                        order_response = requests.post(
                            f"{BASE_URL}/orders/",
                            params={
                                "customer_id": customer_id,
                                "restaurant_id": item["restaurant_id"],
                                "menu_id": item["menu_id"],
                                "quantity": 1,
                                "total_amount": item["price"]
                            }
                        )

                        if order_response.status_code == 200:

                            order_data = order_response.json()

                            st.success(
                                "Recommended food ordered successfully!"
                            )

                            st.write(
                                "Order ID:",
                                order_data["order_id"]
                            )

                        else:

                            st.error(
                                "Unable to order recommended food"
                            )

                            st.code(order_response.text)

                    st.divider()

            else:

                st.info(
                    "No recommendations available yet."
                )

        else:

            st.error(
                f"Unable to load recommendations - "
                f"Status Code: {recommendation_response.status_code}"
            )

    except requests.exceptions.ConnectionError:

        st.error("Unable to connect to FastAPI backend")

else:

    st.info(
        "Please login to view recommendations"
    )


# ---------------- DELIVERY TRACKING ----------------

st.subheader("🚚 Delivery Tracking")

delivery_id = st.number_input(
    "Delivery ID",
    min_value=1,
    value=1,
    step=1
)

if st.button("Check Delivery Status"):

    try:

        delivery_response = requests.get(
            f"{BASE_URL}/deliveries/{delivery_id}"
        )

        if delivery_response.status_code == 200:

            delivery_data = delivery_response.json()

            st.success(
                "Delivery information loaded"
            )

            st.write(
                "🚚 Delivery ID:",
                delivery_data["delivery_id"]
            )

            st.write(
                "📦 Order ID:",
                delivery_data["order_id"]
            )

            st.write(
                "👨‍💼 Delivery Partner:",
                delivery_data["delivery_partner_name"]
            )

            st.write(
                "📱 Phone:",
                delivery_data["phone"]
            )

            st.write(
                "📌 Status:",
                delivery_data["status"]
            )

        elif delivery_response.status_code == 404:

            st.error("Delivery not found")

        else:

            st.error(
                f"Unable to get delivery status - "
                f"Status Code: {delivery_response.status_code}"
            )

    except requests.exceptions.ConnectionError:

        st.error("Unable to connect to FastAPI backend")


# ---------------- PAYMENT ----------------

st.subheader("💳 Payment")

payment_order_id = st.number_input(
    "Payment Order ID",
    min_value=1,
    value=2,
    step=1
)

payment_amount = st.number_input(
    "Amount",
    min_value=1,
    value=150,
    step=1
)

payment_method = st.selectbox(
    "Payment Method",
    ["UPI", "Cash", "Card"]
)

transaction_id = st.text_input(
    "Transaction ID"
)

if st.button("💳 Make Payment"):

    if not transaction_id:

        st.warning(
            "Please enter Transaction ID"
        )

    else:

        try:

            payment_response = requests.post(
                f"{BASE_URL}/payments/",
                params={
                    "order_id": payment_order_id,
                    "payment_method": payment_method,
                    "amount": payment_amount,
                    "transaction_id": transaction_id
                }
            )

            if payment_response.status_code == 200:

                payment_data = payment_response.json()

                st.success(
                    "Payment successful!"
                )

                st.write(
                    "Payment ID:",
                    payment_data["payment_id"]
                )

                st.write(
                    "Order ID:",
                    payment_data["order_id"]
                )

                st.write(
                    "Amount:",
                    payment_data["amount"]
                )

                st.write(
                    "Payment Status:",
                    payment_data["payment_status"]
                )

                st.write(
                    "Transaction ID:",
                    payment_data["transaction_id"]
                )

            elif payment_response.status_code == 404:

                st.error(
                    "Order not found"
                )

            else:

                st.error(
                    f"Payment failed - "
                    f"Status Code: {payment_response.status_code}"
                )

                st.code(payment_response.text)

        except requests.exceptions.ConnectionError:

            st.error(
                "Unable to connect to FastAPI backend"
            )
```
