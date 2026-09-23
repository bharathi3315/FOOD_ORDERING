import streamlit as st
import requests

st.set_page_config(
    page_title="Food Ordering Platform",
    page_icon="🍔"
)

st.title("🍔 Food Ordering and Delivery Platform")

BASE_URL = "https://food-ordering-g7d5.onrender.com"


st.subheader("🔐 Account")

account_type = st.radio(
    "Choose an option",
    ["Login", "Sign Up"],
    horizontal=True
)


# =========================================================
# SIGN UP
# =========================================================

if account_type == "Sign Up":

    st.write("### 📝 Create New Account")

    signup_name = st.text_input(
        "Name",
        key="signup_name"
    )

    signup_email = st.text_input(
        "Email",
        key="signup_email"
    )

    signup_phone = st.text_input(
        "Phone",
        key="signup_phone"
    )

    signup_address = st.text_input(
        "Address",
        key="signup_address"
    )

    signup_password = st.text_input(
        "Password",
        type="password",
        key="signup_password"
    )

    if st.button("📝 Sign Up"):

        if (
            signup_name
            and signup_email
            and signup_phone
            and signup_address
            and signup_password
        ):

            try:

                response = requests.post(
                    f"{BASE_URL}/customers/register",
                    params={
                        "name": signup_name,
                        "email": signup_email,
                        "phone": signup_phone,
                        "address": signup_address,
                        "password": signup_password
                    }
                )

                if response.status_code == 200:

                    st.success(
                        "✅ Registration successful!"
                    )

                    st.info(
                        "Now select Login and login with your email and password."
                    )

                elif response.status_code == 400:

                    st.error(
                        "❌ Email already registered."
                    )

                else:

                    st.error(
                        f"Registration failed - "
                        f"Status Code: {response.status_code}"
                    )

                    st.code(response.text)

            except requests.exceptions.ConnectionError:

                st.error(
                    "Unable to connect to FastAPI backend"
                )

        else:

            st.warning(
                "⚠️ Please fill all the details."
            )


# =========================================================
# LOGIN
# =========================================================

else:

    st.write("### 🔑 Login")

    email = st.text_input(
        "Email",
        key="login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

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

                    st.session_state["customer_id"] = (
                        data["customer_id"]
                    )

                    st.session_state["customer_name"] = (
                        data["name"]
                    )

                    st.session_state["customer_email"] = (
                        data["email"]
                    )

                    st.success(
                        "✅ Login successful!"
                    )

                    st.write(
                        "Welcome,",
                        data["name"]
                    )

                elif response.status_code == 401:

                    st.error(
                        "❌ Invalid email or password"
                    )

                else:

                    st.error(
                        f"Login failed - "
                        f"Status Code: "
                        f"{response.status_code}"
                    )

                    st.code(response.text)

            except requests.exceptions.ConnectionError:

                st.error(
                    "Unable to connect to FastAPI backend"
                )

        else:

            st.warning(
                "Please enter Email and Password"
            )


customer_id = st.session_state.get("customer_id")
# NAVIGATION
if customer_id:
    st.subheader("📌 Navigation")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🛒 Order Food"):
            st.session_state["page"] = "order"

    with col2:
        if st.button("📜 My Orders"):
            st.session_state["page"] = "orders"
if "page" not in st.session_state:
    st.session_state["page"] = "order"


# =========================================================
# FOOD MENU
# =========================================================
if st.session_state.get("page") == "order":
    # FOOD MENU
    st.subheader("🍴 Food Menu")

try:

    response = requests.get(
        f"{BASE_URL}/menus/"
    )

    if response.status_code == 200:

        menus = response.json()

        if menus:

            for item in menus:

                st.write(
                    "🍽️ Food:",
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

                        st.warning(
                            "Please login first"
                        )

                    else:

                        order_response = requests.post(
                            f"{BASE_URL}/orders/",
                            params={
                                "customer_id": customer_id,
                                "restaurant_id": item["restaurant_id"],
                                "menu_id": item["menu_id"],
                                "quantity": quantity,
                                "total_amount": (
                                    item["price"] * quantity
                                )
                            }
                        )

                        if order_response.status_code == 200:

                            order_data = (
                                order_response.json()
                            )

                            st.success(
                                "✅ Order created successfully!"
                            )

                            st.write(
                                "Order ID:",
                                order_data["order_id"]
                            )

                        else:

                            st.error(
                                f"Unable to create order - "
                                f"Status Code: "
                                f"{order_response.status_code}"
                            )

                            st.code(
                                order_response.text
                            )

                st.divider()

        else:

            st.info(
                "No food items available"
            )

    else:

        st.error(
            f"Unable to load food menu - "
            f"Status Code: "
            f"{response.status_code}"
        )

except requests.exceptions.ConnectionError:

    st.error(
        "Unable to connect to FastAPI backend"
    )


# =========================================================
# ORDER HISTORY
# =========================================================
if st.session_state.get("page") == "orders":
    st.subheader("📜 My Order History")

    if customer_id:
        try:
            history_response = requests.get(
                f"{BASE_URL}/orders/customer/"
                f"{customer_id}/history"
            )

            if history_response.status_code == 200:
                history = history_response.json()

                if history:
                    for order in history:
                        st.write("🧾 Order ID:", order["order_id"])
                        st.write("🍽️ Food:", order["food_name"])
                        st.write("🔢 Quantity:", order["quantity"])
                        st.write("💰 Price:", order["price"])
                        st.write("📌 Status:", order["status"])
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


# =========================================================
# RECOMMENDATIONS
# =========================================================

st.subheader("⭐ Recommended For You")

if customer_id:

    try:

        recommendation_response = requests.get(
            f"{BASE_URL}/recommendations/{customer_id}"
        )

        if recommendation_response.status_code == 200:

            recommendations = (
                recommendation_response.json()
            )

            if recommendations:

                st.success(
                    "🍽️ Recommended Food For You"
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
                        "⭐ Score:",
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

                            order_data = (
                                order_response.json()
                            )

                            st.success(
                                "✅ Recommended food "
                                "ordered successfully!"
                            )

                            st.write(
                                "Order ID:",
                                order_data["order_id"]
                            )

                        else:

                            st.error(
                                "Unable to order "
                                "recommended food"
                            )

                            st.code(
                                order_response.text
                            )

                    st.divider()

            else:

                st.warning(
                    "No recommendations available yet."
                )

        else:

            st.error(
                f"Recommendation API failed - "
                f"Status Code: "
                f"{recommendation_response.status_code}"
            )

            st.code(
                recommendation_response.text
            )

    except requests.exceptions.ConnectionError:

        st.error(
            "Unable to connect to FastAPI backend"
        )

else:

    st.info(
        "Please login to view personalized recommendations."
    )


# =========================================================
# DELIVERY TRACKING
# =========================================================

st.subheader("🚚 Delivery Tracking")

if customer_id:

    tracking_order_id = st.number_input(
        "Enter Order ID",
        min_value=1,
        step=1,
        key="tracking_order"
    )

    if st.button("Track Order"):

        try:

            tracking_response = requests.get(
                f"{BASE_URL}/deliveries/order/"
                f"{tracking_order_id}"
            )

            if tracking_response.status_code == 200:

                tracking_data = (
                    tracking_response.json()
                )

                st.success(
                    "✅ Delivery information found"
                )

                st.write(
                    "📦 Order ID:",
                    tracking_data.get("order_id")
                )

                st.write(
                    "🚚 Status:",
                    tracking_data.get("status")
                )

                st.write(
                    "👤 Delivery Partner:",
                    tracking_data.get(
                        "delivery_partner_name"
                    )
                )

                st.write(
                    "📞 Phone:",
                    tracking_data.get("phone")
                )

            elif tracking_response.status_code == 404:

                st.warning(
                    "Delivery not found"
                )

            else:

                st.error(
                    f"Unable to track delivery - "
                    f"Status Code: "
                    f"{tracking_response.status_code}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Unable to connect to FastAPI backend"
            )

else:

    st.info(
        "Please login to track your delivery."
    )


# =========================================================
# PAYMENT
# =========================================================

st.subheader("💳 Payment")

if customer_id:

    payment_order_id = st.number_input(
        "Enter Order ID for Payment",
        min_value=1,
        step=1,
        key="payment_order"
    )

    payment_amount = st.number_input(
        "Payment Amount",
        min_value=1,
        step=1,
        key="payment_amount"
    )

    payment_method = st.selectbox(
        "Payment Method",
        ["UPI", "Card", "Cash"],
        key="payment_method"
    )

    transaction_id = st.text_input(
        "Transaction ID",
        key="transaction_id"
    )

    if st.button("💰 Pay Now"):

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
                        "amount": payment_amount,
                        "payment_method": payment_method,
                        "transaction_id": transaction_id
                    }
                )

                if payment_response.status_code == 200:

                    payment_data = (
                        payment_response.json()
                    )

                    st.success(
                        "✅ Payment successful!"
                    )

                    st.write(
                        "Payment ID:",
                        payment_data.get("payment_id")
                    )

                    st.write(
                        "Order ID:",
                        payment_data.get("order_id")
                    )

                    st.write(
                        "Amount:",
                        payment_data.get("amount")
                    )

                    st.write(
                        "Payment Method:",
                        payment_data.get(
                            "payment_method"
                        )
                    )

                    st.write(
                        "Transaction ID:",
                        payment_data.get(
                            "transaction_id"
                        )
                    )

                    st.write(
                        "Status:",
                        payment_data.get(
                            "payment_status"
                        )
                    )

                else:

                    st.error(
                        f"Payment failed - "
                        f"Status Code: "
                        f"{payment_response.status_code}"
                    )

                    st.code(
                        payment_response.text
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Unable to connect to FastAPI backend"
                )

else:

    st.info(
        "Please login to make payment."
    )