
import streamlit as st
import requests

BASE_URL = "https://food-ordering-1-lwsv.onrender.com"

st.set_page_config(
    page_title="Food Ordering and Delivery Platform",
    page_icon="🍔",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background-color: #fff7f1;
}
.block-container {
    max-width: 1100px;
    padding-top: 1.5rem;
}
.title {
    text-align: center;
    color: #20334d;
    font-size: 36px;
    font-weight: 800;
}
.subtitle {
    text-align: center;
    color: #858b98;
    margin-bottom: 25px;
}
.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(90deg, #ff873e, #ff602d);
    color: white;
    border: none;
    border-radius: 10px;
    min-height: 42px;
    width: 100%;
    font-weight: 600;
}
.food-card {
    background: white;
    border: 1px solid #f0ded1;
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------
defaults = {
    "page": "signup",
    "logged_in": False,
    "customer_id": None,
    "customer_name": "",
    "cart": {},
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def show_api_error(response, action):
    try:
        detail = response.json().get("detail", response.text)
    except (ValueError, AttributeError):
        detail = response.text

    st.error(f"{action} failed: HTTP {response.status_code}")
    st.code(str(detail))


# ---------------- HEADER ----------------
st.markdown(
    '<div class="title">🍔 Food Ordering and Delivery Platform</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Fresh food, delivered with love!</div>',
    unsafe_allow_html=True
)


# ==================================================
# SIGNUP
# ==================================================
if not st.session_state.logged_in and st.session_state.page == "signup":

    st.subheader("📝 Create New Account")

    with st.form("signup_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        address = st.text_area("Address")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input(
            "Confirm Password", type="password"
        )

        signup_clicked = st.form_submit_button("Create Account")

    if signup_clicked:
        if not all([
            name.strip(),
            email.strip(),
            phone.strip(),
            address.strip(),
            password,
            confirm_password
        ]):
            st.warning("Please fill in all fields.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        else:
            try:
                response = requests.post(
                    f"{BASE_URL}/customers/register",
                    params={
                        "name": name.strip(),
                        "email": email.strip(),
                        "phone": phone.strip(),
                        "address": address.strip(),
                        "password": password,
                    },
                    timeout=15,
                )

                if response.status_code in (200, 201):
                    st.success("Account created successfully!")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    show_api_error(response, "Registration")

            except requests.RequestException as exc:
                st.error(f"Backend connection failed: {exc}")

    if st.button("🔐 Already have an account? Login"):
        st.session_state.page = "login"
        st.rerun()


# ==================================================
# LOGIN
# ==================================================
elif not st.session_state.logged_in and st.session_state.page == "login":

    st.subheader("🔐 Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_clicked = st.form_submit_button("Login")

    if login_clicked:
        if not email.strip() or not password:
            st.warning("Enter your email and password.")

        else:
            try:
                response = requests.post(
                    f"{BASE_URL}/customers/login",
                    json={
                        "email": email.strip(),
                        "password": password,
                    },
                    timeout=15,
                )

                if response.status_code == 200:
                    data = response.json()
                    customer_id = data.get("customer_id")

                    if customer_id is None:
                        st.error("Customer ID missing in login response.")
                    else:
                        st.session_state.customer_id = customer_id
                        st.session_state.customer_name = data.get(
                            "name", email.strip()
                        )
                        st.session_state.logged_in = True
                        st.session_state.page = "home"
                        st.rerun()
                else:
                    show_api_error(response, "Login")

            except requests.RequestException as exc:
                st.error(f"Backend connection failed: {exc}")

    if st.button("📝 Create New Account"):
        st.session_state.page = "signup"
        st.rerun()


# ==================================================
# HOME
# ==================================================
else:

    st.subheader(
        f"Welcome, {st.session_state.customer_name}! 🍽️"
    )

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.customer_id = None
        st.session_state.customer_name = ""
        st.session_state.cart = {}
        st.session_state.page = "login"
        st.rerun()

    # ---------------- FETCH MENU ----------------
    try:
        menu_response = requests.get(
            f"{BASE_URL}/menus/",
            timeout=15,
        )
        menu_response.raise_for_status()
        menu_items = menu_response.json()

        if not isinstance(menu_items, list):
            menu_items = []
            st.warning("Unexpected menu response from backend.")

    except (requests.RequestException, ValueError) as exc:
        menu_items = []
        st.error(f"Menu loading failed: {exc}")

    # Lookup table for food details
    menu_lookup = {
        food.get("menu_id"): food
        for food in menu_items
        if food.get("menu_id") is not None
    }

    # ---------------- POPULAR FOODS ----------------
    st.markdown("### 🍕 Popular Foods")

    if not menu_items:
        st.info("No food items available.")

    else:
        columns = st.columns(3)

        for index, food in enumerate(menu_items):
            food_id = food.get("menu_id")
            food_name = food.get("food_name", "Food")
            price = float(food.get("price", 0))
            category = food.get("category", "Food")

            with columns[index % 3]:
                st.markdown(
                    f"""
                    <div class="food-card">
                        <h3>🍽️ {food_name}</h3>
                        <p>Category: {category}</p>
                        <h4>₹{price:.2f}</h4>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    "➕ Add to Cart",
                    key=f"add_{food_id}_{index}",
                ):
                    if food_id is None:
                        st.error("Menu item ID is missing.")
                    elif food.get("restaurant_id") is None:
                        st.error("Restaurant ID is missing for this food.")
                    else:
                        cart = st.session_state.cart

                        if food_id in cart:
                            cart[food_id]["quantity"] += 1
                        else:
                            cart[food_id] = {
                                "menu_id": int(food_id),
                                "food_name": food_name,
                                "price": price,
                                "quantity": 1,
                                "restaurant_id": food["restaurant_id"],
                            }

                        st.session_state.cart = cart
                        st.rerun()

    # ---------------- CART ----------------
    st.divider()
    st.subheader("🛒 Your Cart")

    if not st.session_state.cart:
        st.info("Your cart is empty. Add some food!")

    else:
        for food_id in list(st.session_state.cart.keys()):
            item = st.session_state.cart[food_id]
            subtotal = item["price"] * item["quantity"]

            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.write(item["food_name"])
                st.caption(f"₹{item['price']:.2f} each")

            with col2:
                st.write(f"Quantity: {item['quantity']}")

            with col3:
                if st.button("+", key=f"plus_{food_id}"):
                    st.session_state.cart[food_id]["quantity"] += 1
                    st.rerun()

                if st.button("-", key=f"minus_{food_id}"):
                    st.session_state.cart[food_id]["quantity"] -= 1

                    if st.session_state.cart[food_id]["quantity"] <= 0:
                        del st.session_state.cart[food_id]

                    st.rerun()

            with col4:
                if st.button("Remove", key=f"remove_{food_id}"):
                    del st.session_state.cart[food_id]
                    st.rerun()

            st.write(f"Subtotal: ₹{subtotal:.2f}")

        cart_total = sum(
            item["price"] * item["quantity"]
            for item in st.session_state.cart.values()
        )

        st.markdown(f"### Cart Total: ₹{cart_total:.2f}")

        clear_col, order_col = st.columns(2)

        with clear_col:
            if st.button("🧹 Clear Cart"):
                st.session_state.cart = {}
                st.rerun()

        # ---------------- PLACE ORDER ----------------
        with order_col:
            if st.button("🛍️ Place Order", type="primary"):

                customer_id = st.session_state.customer_id
                current_cart = st.session_state.cart

                if not customer_id:
                    st.error("Please log in again.")

                elif not current_cart:
                    st.warning("Your cart is empty.")

                else:
                    restaurant_ids = {
                        item.get("restaurant_id")
                        for item in current_cart.values()
                    }

                    if None in restaurant_ids or len(restaurant_ids) != 1:
                        st.error(
                            "Select food from one restaurant per order."
                        )

                    else:
                        restaurant_id = next(iter(restaurant_ids))

                        order_items = [
                            {
                                "menu_id": int(item["menu_id"]),
                                "quantity": int(item["quantity"]),
                            }
                            for item in current_cart.values()
                        ]

                        total_amount = int(round(cart_total))

                        try:
                            order_response = requests.post(
                                f"{BASE_URL}/orders/",
                                params={
                                    "customer_id": int(customer_id),
                                    "restaurant_id": int(restaurant_id),
                                    "total_amount": total_amount,
                                },
                                json=order_items,
                                timeout=20,
                            )

                            if order_response.status_code in (200, 201):
                                result = order_response.json()

                                st.success("Order placed successfully!")
                                st.write("Order ID:", result.get("order_id"))
                                st.write("Status:", result.get("status"))
                                st.write(
                                    "Total:",
                                    f"₹{result.get('total_amount', total_amount)}"
                                )

                                st.markdown("#### 🍽️ Ordered Items")

                                for item in result.get("items", []):
                                    food = menu_lookup.get(item["menu_id"])
                                    food_name = (
                                        food.get("food_name", "Food")
                                        if food else f"Menu ID: {item['menu_id']}"
                                    )

                                    st.write(
                                        f"{food_name} | "
                                        f"Quantity: {item['quantity']} | "
                                        f"Price: ₹{item['price']}"
                                    )

                                st.session_state.cart = {}

                            else:
                                show_api_error(order_response, "Place order")

                        except requests.RequestException as exc:
                            st.error(f"Order request failed: {exc}")

    # ---------------- RECOMMENDATIONS ----------------
    st.divider()
    st.subheader("⭐ Recommended For You")

    customer_id = st.session_state.customer_id

    try:
        recommendation_response = requests.get(
            f"{BASE_URL}/recommendations/{customer_id}",
            timeout=10,
        )

        if recommendation_response.status_code == 200:
            recommendations = recommendation_response.json()

            if recommendations:
                st.caption("Suggestions based on your order history")

                shown_count = 0
                columns = st.columns(3)

                for index, recommendation in enumerate(recommendations):
                    if not isinstance(recommendation, dict):
                        continue

                    menu_id = recommendation.get("menu_id")
                    food = menu_lookup.get(menu_id)

                    if food is None:
                        continue

                    food_name = food.get("food_name", "Food")
                    price = float(food.get("price", 0))
                    category = food.get("category", "Food")
                    score = recommendation.get("score", 0)

                    with columns[shown_count % 3]:
                        st.markdown(
                            f"""
                            <div class="food-card">
                                <h3>🍽️ {food_name}</h3>
                                <p>Category: {category}</p>
                                <h4>₹{price:.2f}</h4>
                                <p>⭐ Recommendation score: {score}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if st.button(
                            "➕ Add to Cart",
                            key=f"recommend_{menu_id}_{index}",
                        ):
                            restaurant_id = food.get("restaurant_id")

                            if restaurant_id is None:
                                st.error("Restaurant ID missing.")
                            else:
                                cart = st.session_state.cart

                                if menu_id in cart:
                                    cart[menu_id]["quantity"] += 1
                                else:
                                    cart[menu_id] = {
                                        "menu_id": int(menu_id),
                                        "food_name": food_name,
                                        "price": price,
                                        "quantity": 1,
                                        "restaurant_id": restaurant_id,
                                    }

                                st.session_state.cart = cart
                                st.rerun()

                    shown_count += 1

                if shown_count == 0:
                    st.info(
                        "Recommended items are not available in the current menu."
                    )

            else:
                st.info(
                    "Recommendations will appear when data is available."
                )

        else:
            st.info("Recommendations are not available yet.")

    except requests.RequestException:
        st.info("Could not load recommendations right now.")
