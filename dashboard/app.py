
import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="SmartStock | Inventory Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM DARK UI ----------

st.markdown("""
<style>
.stApp {
    background: #0B1120;
}
[data-testid="stSidebar"] {
    background: #111B2E;
    border-right: 1px solid #26344A;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: #F1F5F9 !important;
}
p, label, .stMarkdown {
    color: #CBD5E1;
}
[data-testid="stMetric"] {
    background: #151F32;
    border: 1px solid #26344A;
    padding: 18px;
    border-radius: 12px;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF;
}
.stButton button {
    background: #7C3AED;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}
.stButton button:hover {
    background: #6D28D9;
    color: white;
    border: none;
}
div[data-testid="stForm"] {
    background: #151F32;
    padding: 20px;
    border: 1px solid #26344A;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# ---------- API HELPERS ----------

def api_get(path):
    response = requests.get(f"{API_URL}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


def api_post(path, payload):
    response = requests.post(
        f"{API_URL}{path}",
        json=payload,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def api_put(path, payload):
    response = requests.put(
        f"{API_URL}{path}",
        json=payload,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def show_api_error(error):
    if isinstance(error, requests.HTTPError):
        try:
            detail = error.response.json().get("detail", error.response.text)
        except Exception:
            detail = error.response.text
        st.error(f"API error: {detail}")
    else:
        st.error(f"Request failed: {error}")


# ---------- HEADER ----------

st.title("📦 SmartStock")
st.caption("INVENTORY INTELLIGENCE  /  STOCKOUT PREDICTION")

with st.sidebar:
    st.markdown("# 📦 SmartStock")
    st.caption("Inventory Intelligence Platform")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Products",
            "Suppliers",
            "Record Sale",
            "Stock Management",
            "Stockout Risk Center",
            "ML Predictions"
        ]
    )

    st.divider()
    st.markdown("**System status**")
    st.success("Dashboard connected")


# ---------- LOAD INVENTORY ----------

try:
    inventory = api_get("/inventory/")
    df = pd.DataFrame(inventory)

except requests.RequestException as error:
    st.error("Cannot connect to the FastAPI backend.")
    st.code("uvicorn app.main:app --reload")
    st.stop()

if df.empty:
    st.warning("No inventory records found.")
    st.stop()

required_columns = {
    "product_id", "name", "quantity_on_hand", "reorder_level"
}

if not required_columns.issubset(df.columns):
    st.error("The inventory API response is missing expected fields.")
    st.write(df)
    st.stop()

df["quantity_on_hand"] = pd.to_numeric(
    df["quantity_on_hand"], errors="coerce"
).fillna(0)

df["reorder_level"] = pd.to_numeric(
    df["reorder_level"], errors="coerce"
).fillna(0)

low_df = df[df["quantity_on_hand"] <= df["reorder_level"]]


# ---------- OVERVIEW ----------

if page == "Overview":

    st.subheader("Business Overview")
    st.caption("Live inventory position and stock health")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Products", df["product_id"].nunique())
    c2.metric("Total Stock Units", int(df["quantity_on_hand"].sum()))
    c3.metric("Low Stock Items", len(low_df))
    c4.metric(
        "Healthy Stock Items",
        len(df) - len(low_df)
    )

    st.divider()

    left, right = st.columns([1.6, 1])

    with left:
        st.subheader("Stock Distribution")

        fig = px.bar(
            df,
            x="name",
            y="quantity_on_hand",
            color="quantity_on_hand",
            color_continuous_scale="Purples",
            template="plotly_dark",
            labels={
                "name": "Product",
                "quantity_on_hand": "Available Units"
            }
        )

        fig.update_layout(
            paper_bgcolor="#0B1120",
            plot_bgcolor="#0B1120",
            margin=dict(l=10, r=10, t=20, b=10),
            coloraxis_showscale=False
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Inventory Health")

        healthy = len(df) - len(low_df)

        fig = px.pie(
            names=["Healthy", "Low Stock"],
            values=[healthy, len(low_df)],
            hole=0.68,
            color_discrete_sequence=["#8B5CF6", "#F59E0B"],
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="#0B1120",
            margin=dict(l=5, r=5, t=10, b=10),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("⚠️ Stock Alerts")

    if low_df.empty:
        st.success("All products are above their reorder levels.")
    else:
        for _, item in low_df.iterrows():
            st.warning(
                f"{item['name']} — "
                f"{int(item['quantity_on_hand'])} units remaining "
                f"(reorder level: {int(item['reorder_level'])})"
            )

    st.subheader("Current Inventory")
    st.dataframe(df, use_container_width=True, hide_index=True)


# ---------- PRODUCTS ----------


# ---------- PRODUCTS ----------

elif page == "Products":

    st.subheader("Product Management")
    st.caption("Add new products to your inventory catalogue")

    try:
        suppliers = api_get("/suppliers/")

        supplier_options = {
            f"{s['name']} — {s['lead_time_days']} days lead time":
            s["supplier_id"]
            for s in suppliers
        }

        if not supplier_options:
            st.warning("No suppliers available. Add a supplier first.")

        else:
            with st.form("add_product_form"):

                name = st.text_input("Product name")
                sku = st.text_input("SKU (Unique ID of Product)")
                category = st.text_input("Category")
                price = st.number_input(
                    "Unit price",
                    min_value=0.0,
                    step=1.0
                )

                selected_supplier = st.selectbox(
                    "Select Supplier",
                    options=list(supplier_options.keys())
                )

                initial_stock = st.number_input(
                    "Initial stock quantity",
                    min_value=0,
                    step=1
                )

                reorder_level = st.number_input(
                    "Reorder level",
                    min_value=0,
                    value=10,
                    step=1
                )

                safety_stock = st.number_input(
                    "Safety stock",
                    min_value=0,
                    value=5,
                    step=1
                )

                submitted = st.form_submit_button(
                    "➕ Add Product",
                    use_container_width=True
                )

                if submitted:

                    if not name.strip() or not sku.strip():
                        st.error("Product name and SKU are required.")

                    else:
                        try:
                            payload = {
                                "name": name.strip(),
                                "sku": sku.strip(),
                                "category": category.strip() or None,
                                "unit_price": price,
                                "supplier_id": supplier_options[selected_supplier]
                            }

                            product = api_post("/products/", payload)
                            new_id = product["product_id"]

                            inventory_payload = {
                                "product_id": new_id,
                                "quantity_on_hand": int(initial_stock),
                                "reorder_level": int(reorder_level),
                                "safety_stock": int(safety_stock)
                            }

                            api_post("/inventory/", inventory_payload)

                            st.success(f"{name} added successfully!")
                            st.rerun()

                        except requests.RequestException as error:
                            show_api_error(error)

    except requests.RequestException as error:
        show_api_error(error)

    st.divider()
    st.subheader("Product Catalogue")

    try:
        products = api_get("/products/")
        st.dataframe(
            pd.DataFrame(products),
            use_container_width=True,
            hide_index=True
        )
    except requests.RequestException as error:
        show_api_error(error)


# ---------- SUPPLIER MANAGEMENT ----------

elif page == "Suppliers":

    st.subheader("Supplier Management")
    st.caption("Register and manage your inventory suppliers")

    st.markdown("### Add New Supplier")

    with st.form("add_supplier_form"):

        supplier_name = st.text_input("Supplier Name")

        contact_email = st.text_input("Contact Email")

        phone = st.text_input("Phone Number")

        lead_time = st.number_input(
            "Delivery Lead Time (Days)",
            min_value=0,
            value=3,
            step=1
        )

        submitted = st.form_submit_button(
            "➕ Add Supplier",
            use_container_width=True
        )

        if submitted:

            if not supplier_name.strip():
                st.error("Supplier name is required.")

            else:
                try:
                    payload = {
                        "name": supplier_name.strip(),
                        "contact_email": contact_email.strip() or None,
                        "phone": phone.strip() or None,
                        "lead_time_days": int(lead_time)
                    }

                    result = api_post("/suppliers/", payload)

                    st.success(
                        f"{result['name']} added successfully!"
                    )

                    st.rerun()

                except requests.RequestException as error:
                    show_api_error(error)

    st.divider()

    st.markdown("### Registered Suppliers")

    try:
        suppliers = api_get("/suppliers/")

        if suppliers:
            supplier_df = pd.DataFrame(suppliers)

            st.metric("Total Suppliers", len(suppliers))

            st.dataframe(
                supplier_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No suppliers registered yet.")

    except requests.RequestException as error:
        show_api_error(error)




# ---------- RECORD SALE ----------

elif page == "Record Sale":

    st.subheader("Sales Management")
    st.caption("Record a sale and automatically deduct stock")

    with st.form("sale_form"):

        product_options = {
            f"{row['name']} (ID: {int(row['product_id'])})":
            int(row["product_id"])
            for _, row in df.iterrows()
        }

        selected = st.selectbox(
            "Select product",
            list(product_options.keys())
        )

        quantity = st.number_input(
            "Quantity sold",
            min_value=1,
            step=1
        )

        submitted = st.form_submit_button(
            "💰 Record Sale",
            use_container_width=True
        )

        if submitted:
            try:
                result = api_post(
                    "/sales/",
                    {
                        "product_id": product_options[selected],
                        "quantity": int(quantity)
                    }
                )

                st.success("Sale recorded and inventory updated!")
                st.json(result)
                st.rerun()

            except requests.RequestException as error:
                show_api_error(error)


# ---------- STOCK MANAGEMENT ----------

elif page == "Stock Management":

    st.subheader("Stock Management")
    st.caption("Manually correct or update inventory quantities")

    with st.form("stock_update_form"):

        product_options = {
            f"{row['name']} (ID: {int(row['product_id'])})":
            int(row["product_id"])
            for _, row in df.iterrows()
        }

        selected = st.selectbox(
            "Select product",
            list(product_options.keys())
        )

        current_id = product_options[selected]
        current_stock = int(
            df.loc[df["product_id"] == current_id, "quantity_on_hand"].iloc[0]
        )

        st.info(f"Current stock: {current_stock} units")

        new_stock = st.number_input(
            "New stock quantity",
            min_value=0,
            value=current_stock,
            step=1
        )

        submitted = st.form_submit_button(
            "Update Stock",
            use_container_width=True
        )

        if submitted:
            try:
                result = api_put(
                    f"/inventory/{current_id}",
                    {"quantity_on_hand": int(new_stock)}
                )

                st.success("Stock updated successfully!")
                st.rerun()

            except requests.RequestException as error:
                show_api_error(error)

    st.divider()
    st.subheader("Current Stock Levels")
    st.dataframe(
        df[
            ["product_id", "name", "quantity_on_hand", "reorder_level"]
        ],
        use_container_width=True,
        hide_index=True
    )

# ---------- STOCKOUT RISK CENTER ----------

elif page == "Stockout Risk Center":

    st.subheader("🚨 Stockout Risk Center")
    st.caption("Store-wide inventory risk analysis and intelligent reorder planning")

    # Refresh analytics
    if st.button("🔄 Refresh Risk Analysis"):
        st.rerun()

    try:
        risk_data = api_get("/analytics/stockout-risk")
        risk_df = pd.DataFrame(risk_data)

    except requests.RequestException as error:
        show_api_error(error)
        st.stop()

    if risk_df.empty:
        st.info("No inventory analytics available.")
        st.stop()

    # Risk counts
    critical_count = len(risk_df[risk_df["risk_level"] == "CRITICAL"])
    high_count = len(risk_df[risk_df["risk_level"] == "HIGH"])
    low_count = len(risk_df[risk_df["risk_level"] == "LOW"])
    unknown_count = len(risk_df[risk_df["risk_level"] == "UNKNOWN"])

    reorder_count = int(risk_df["reorder_recommended"].sum())
     # Prepare downloadable reorder report
    reorder_df = risk_df[
        risk_df["reorder_recommended"]
    ].copy()

    st.download_button(
        label="📥 Download Reorder Report",
        data=reorder_df.to_csv(index=False).encode("utf-8"),
        file_name="inventory_reorder_report.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.markdown("### Inventory Risk Overview")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Critical", critical_count)
    c2.metric("High Risk", high_count)
    c3.metric("Low Risk", low_count)
    c4.metric("Unknown", unknown_count)
    c5.metric("Reorder Needed", reorder_count)

    

    st.divider()

    # Urgent products
    st.markdown("### ⚠️ Products Requiring Attention")

    urgent_df = risk_df[
        risk_df["risk_level"].isin(["CRITICAL", "HIGH"])
        | risk_df["reorder_recommended"]
    ].copy()

    if urgent_df.empty:
        st.success("No products currently require urgent attention.")
    else:
        urgent_df = urgent_df.sort_values(
            by="estimated_days_remaining",
            na_position="last"
        )

        display_columns = [
            "product_name",
            "current_stock",
            "average_daily_demand",
            "estimated_days_remaining",
            "lead_time_days",
            "reorder_point",
            "risk_level",
            "reorder_recommended"
        ]

        st.dataframe(
            urgent_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # Risk distribution chart
    st.markdown("### Risk Distribution")

    risk_chart = (
        risk_df["risk_level"]
        .value_counts()
        .reindex(["CRITICAL", "HIGH", "LOW", "UNKNOWN"], fill_value=0)
        .reset_index()
    )

    risk_chart.columns = ["Risk Level", "Products"]

    fig = px.pie(
        risk_chart,
        names="Risk Level",
        values="Products",
        hole=0.65,
        color="Risk Level",
        color_discrete_map={
            "CRITICAL": "#EF4444",
            "HIGH": "#F59E0B",
            "LOW": "#10B981",
            "UNKNOWN": "#64748B"
        },
        template="plotly_dark"
    )

    fig.update_layout(
        paper_bgcolor="#0B1120",
        plot_bgcolor="#0B1120",
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Complete inventory risk table
    st.markdown("### Complete Inventory Risk Analysis")

    st.dataframe(
        risk_df,
        use_container_width=True,
        hide_index=True
    )



# ---------- ML PREDICTIONS ----------

elif page == "ML Predictions":

    st.subheader("🤖 Demand Forecast & Stock Intelligence")
    st.caption("Machine learning-powered demand prediction and reorder analysis")

    product_options = {
        f"{row['name']} (ID: {int(row['product_id'])})":
        int(row["product_id"])
        for _, row in df.iterrows()
    }

    selected = st.selectbox(
        "Select product",
        list(product_options.keys())
    )

    product_id = product_options[selected]

    if st.button("Generate ML Forecast", use_container_width=True):

        try:
            # Fetch both prediction and recommendation
            prediction = api_get(
                f"/predictions/demand/{product_id}"
            )

            recommendation = api_get(
                f"/recommendations/reorder/{product_id}"
            )

            st.session_state["ml_prediction"] = prediction
            st.session_state["ml_recommendation"] = recommendation
            st.session_state["ml_product_id"] = product_id

        except requests.RequestException as error:
            show_api_error(error)

    # Display results only for the product that was forecast
    if (
        "ml_prediction" in st.session_state
        and st.session_state.get("ml_product_id") == product_id
    ):

        prediction = st.session_state["ml_prediction"]
        recommendation = st.session_state["ml_recommendation"]

        st.divider()
                # Forecast intelligence
        st.markdown("### Forecast Intelligence")

        source = prediction.get("forecast_source", "unknown")
        history_days = prediction.get("history_days", 0)

        source_labels = {
            "ml_model": "Machine Learning Model",
            "category_average": "Category Average",
            "store_average": "Store Average",
            "no_store_sales": "No Store Sales Available"
        }

        source_descriptions = {
            "ml_model": "Prediction generated using the trained demand model.",
            "category_average": "Estimated using sales from products in the same category.",
            "store_average": "Estimated using overall store demand.",
            "no_store_sales": "No sales data available to estimate demand."
        }

        source_label = source_labels.get(source, source)

        st.info(
            f"Forecast method: {source_label}\\n\\n"
            f"{source_descriptions.get(source, 'Forecast source unavailable.')}"
        )

        st.caption(
            f"Available product sales history: {history_days} calendar days"
        )

        st.markdown("### Forecast Results")

        # KPI cards
        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Predicted Daily Demand",
            f"{prediction['predicted_daily_demand']:.2f} units"
        )

        c2.metric(
            "Current Stock",
            f"{recommendation['current_stock']} units"
        )

        c3.metric(
            "Days Remaining",
            f"{recommendation['estimated_days_remaining']:.2f}"
            if recommendation["estimated_days_remaining"] is not None
            else "Unknown"
        )

        c4.metric(
            "Reorder Point",
            f"{recommendation['reorder_point']:.2f} units"
        )

        st.divider()

        # Risk and reorder status
        left, right = st.columns(2)

        with left:
            st.markdown("### Stock Risk")

            risk = recommendation["stock_risk"]

            risk_colors = {
                "LOW": "#10B981",
                "HIGH": "#F59E0B",
                "CRITICAL": "#EF4444",
                "UNKNOWN": "#94A3B8"
            }

            risk_color = risk_colors.get(risk, "#94A3B8")

            st.markdown(
                f"""
                <div style="
                    background:#151F32;
                    border:1px solid {risk_color};
                    border-radius:12px;
                    padding:22px;
                    text-align:center;">
                    <div style="color:#94A3B8;font-size:14px;">
                        CURRENT STOCK RISK
                    </div>
                    <div style="
                        color:{risk_color};
                        font-size:30px;
                        font-weight:700;
                        margin-top:8px;">
                        {risk}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with right:
            st.markdown("### Reorder Decision")

            if recommendation["reorder_recommended"]:
                st.error("⚠️ Reordering is recommended.")

                st.metric(
                    "Minimum Stock Shortfall",
                    f"{recommendation['minimum_stock_shortfall']} units"
                )
            else:
                st.success("✓ No immediate reorder required.")

                st.metric(
                    "Minimum Stock Shortfall",
                    "0 units"
                )

        st.divider()

        # Stock vs reorder point chart
        st.markdown("### Stock Position Analysis")

        chart_df = pd.DataFrame({
            "Metric": ["Current Stock", "Reorder Point", "Safety Stock"],
            "Units": [
                recommendation["current_stock"],
                recommendation["reorder_point"],
                recommendation["safety_stock"]
            ]
        })

        fig = px.bar(
            chart_df,
            x="Metric",
            y="Units",
            color="Metric",
            color_discrete_sequence=[
                "#8B5CF6",
                "#F59E0B",
                "#06B6D4"
            ],
            template="plotly_dark",
            text_auto=".2f"
        )

        fig.update_layout(
            paper_bgcolor="#0B1120",
            plot_bgcolor="#0B1120",
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10),
            yaxis_title="Units",
            xaxis_title=""
        )

        st.plotly_chart(fig, use_container_width=True)

        # Supporting details
        st.markdown("### Recommendation Details")

        d1, d2, d3 = st.columns(3)

        d1.metric(
            "Supplier Lead Time",
            f"{recommendation['supplier_lead_time_days']} days"
        )

        d2.metric(
            "Safety Stock",
            f"{recommendation['safety_stock']} units"
        )

        d3.metric(
            "Forecast Date",
            prediction["prediction_date"]
        )

        # Estimated stock runway
        daily_demand = prediction["predicted_daily_demand"]
        current_stock = recommendation["current_stock"]

        if daily_demand > 0:
            st.markdown("### Estimated Stock Runway")

            runway_days = min(
                int(recommendation["estimated_days_remaining"] or 0),
                30
            )

            runway_df = pd.DataFrame({
                "Day": list(range(runway_days + 1)),
                "Projected Stock": [
                    max(0, current_stock - daily_demand * day)
                    for day in range(runway_days + 1)
                ]
            })

            runway_fig = px.line(
                runway_df,
                x="Day",
                y="Projected Stock",
                markers=True,
                template="plotly_dark",
                title="Illustrative stock depletion"
            )

            runway_fig.update_traces(
                line=dict(color="#A78BFA", width=3)
            )

            runway_fig.update_layout(
                paper_bgcolor="#0B1120",
                plot_bgcolor="#0B1120",
                xaxis_title="Days from today",
                yaxis_title="Estimated stock units"
            )

            st.plotly_chart(
                runway_fig,
                use_container_width=True
            )

            st.caption(
                "This runway is a simple projection assuming the predicted "
                "daily demand remains constant. It is not a separate "
                "multi-day ML forecast."
            )

        st.divider()

        st.info(
            "Model limitation: the current ML model was trained on synthetic "
            "sales data. Treat these forecasts as experimental until the "
            "model is validated using representative real sales history."
        )


