
import streamlit as st
import pandas as pd
from datetime import datetime

# =========================================================
# ECL MATERIAL REQUIREMENT PLANNER
# Three-page workflow:
# 1. Required Components
# 2. Stock Entry
# 3. Final Business Requirement
# =========================================================

st.set_page_config(
    page_title="ECL Material Requirement Planner",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# PRODUCT DATA
# -----------------------------

PRODUCTS = {
    "SHINE NEW": {
        "category": "Stators / Wire Harness",
        "status": "READY",
        "description": "Wire Shine Stator harness - new model using Cup Blue CB104.",
        "components": [
            {"Material": "White Coupler", "Specification": "White connector / coupler", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "Terminal F Lock 6.4", "Specification": "6.4 mm female lock terminal", "Unit": "pcs", "Required Per Unit": 2},
            {"Material": "Terminal CB104 Bullet", "Specification": "CB104 bullet terminal", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "Cup Blue CB104", "Specification": "Blue CB104 cup/cap", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "Black Grommet", "Specification": "Black grommet", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "Black PVC Sleeve", "Specification": "150 mm, size 6 × 7", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "Yellow Silicone Sleeve", "Specification": "5 mm sleeve, 70 mm length", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "PVC Wire 2×16/38 Green", "Specification": "470 mm per harness", "Unit": "mm", "Required Per Unit": 470},
            {"Material": "PVC Wire Green", "Specification": "300 mm per harness", "Unit": "mm", "Required Per Unit": 300},
            {"Material": "Blue Wire with Yellow Line", "Specification": "300 mm per harness", "Unit": "mm", "Required Per Unit": 300},
            {"Material": "White Wire", "Specification": "360 mm per harness", "Unit": "mm", "Required Per Unit": 360},
        ],
    },
    "SHINE OLD": {
        "category": "Stators / Wire Harness",
        "status": "READY",
        "description": "Wire Shine Stator harness - old model using Black Cap.",
        "components": [
            {"Material": "White Coupler", "Specification": "White connector / coupler", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "Terminal F Lock", "Specification": "F Lock terminal", "Unit": "pcs", "Required Per Unit": 2},
            {"Material": "Terminal CB104 Bullet", "Specification": "CB104 bullet terminal", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "Black Cap", "Specification": "Black cap", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "Black Grommet", "Specification": "Black grommet", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "Black PVC Sleeve", "Specification": "150 mm, size 6 × 7", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "Yellow Silicone Sleeve", "Specification": "5 mm sleeve, 70 mm length", "Unit": "pcs", "Required Per Unit": 1},
            {"Material": "PVC Wire 2×16/38 Green", "Specification": "330 mm per harness", "Unit": "mm", "Required Per Unit": 330},
            {"Material": "PVC Wire Green", "Specification": "550 mm per harness", "Unit": "mm", "Required Per Unit": 550},
            {"Material": "Blue Wire with Yellow Line", "Specification": "325 mm per harness", "Unit": "mm", "Required Per Unit": 325},
            {"Material": "White Wire", "Specification": "550 mm per harness", "Unit": "mm", "Required Per Unit": 550},
        ],
    },

    # Catalogue placeholders until internal component/BOM sheets are provided.
    "Horns DC - Windtone Black": {"category": "Horns DC", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Horns DC - Windtone": {"category": "Horns DC", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Horns DC - 2W": {"category": "Horns DC", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Horns DC - 2W HD": {"category": "Horns DC", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Horns AC - 2W 6V & 12V Flower Type": {"category": "Horns AC", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Horns AC - 2W 6V & 12V Milano Type": {"category": "Horns AC", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Horns AC - 2W 6V & 12V Super XL": {"category": "Horns AC", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Stators - 2W": {"category": "Stators", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Source Coils - 2W": {"category": "Source Coils", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Light Coils - 2W": {"category": "Light Coils", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Ignition Coils - 2W": {"category": "Ignition Coils", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Igniters - 2W": {"category": "Igniters", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "CDI Units - 2W CT 100": {"category": "CDI Units", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Regulator Rectifiers - 2W": {"category": "Regulator Rectifiers", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Starter Relays - 2W Old Model": {"category": "Starter Relays", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Starter Relays - 2W 12V": {"category": "Starter Relays", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Flashers - 2W": {"category": "Flashers", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
    "Buzzers - 2W": {"category": "Buzzers", "status": "TO BE UPDATED SOON", "description": "Component list pending.", "components": []},
}

# -----------------------------
# SESSION STATE
# -----------------------------

if "selected_product" not in st.session_state:
    st.session_state.selected_product = "SHINE NEW"

if "production_quantity" not in st.session_state:
    st.session_state.production_quantity = 1000

if "stock_values" not in st.session_state:
    st.session_state.stock_values = {}

# -----------------------------
# HELPERS
# -----------------------------

def stock_key(product_name, material, specification, unit):
    return f"{product_name}|{material}|{specification}|{unit}"

def format_qty(value, unit):
    value = float(value or 0)
    if unit == "pcs":
        return f"{value:,.0f} pcs"
    if unit == "mm":
        return f"{value:,.0f} mm / {value / 1000:,.2f} m"
    return f"{value:,.2f} {unit}"

def product_has_bom(product_name):
    return len(PRODUCTS[product_name]["components"]) > 0

def required_df(product_name, quantity):
    product = PRODUCTS[product_name]
    rows = []
    for item in product["components"]:
        total_needed = float(item["Required Per Unit"]) * float(quantity)
        rows.append({
            "Material": item["Material"],
            "Specification": item["Specification"],
            "Unit": item["Unit"],
            "Required for 1 Piece": float(item["Required Per Unit"]),
            "Total Required": total_needed,
        })
    return pd.DataFrame(rows)

def required_display_df(df):
    if df.empty:
        return df
    display = df.copy()
    display["Required for 1 Piece"] = [
        format_qty(v, u) for v, u in zip(display["Required for 1 Piece"], display["Unit"])
    ]
    display["Total Required"] = [
        format_qty(v, u) for v, u in zip(display["Total Required"], display["Unit"])
    ]
    return display

def stock_input_df(product_name, quantity):
    df = required_df(product_name, quantity)
    if df.empty:
        return df

    stock_list = []
    for _, row in df.iterrows():
        key = stock_key(product_name, row["Material"], row["Specification"], row["Unit"])
        stock_list.append(float(st.session_state.stock_values.get(key, 0) or 0))

    df["Stock Available"] = stock_list
    return df

def save_stock(product_name, edited_df):
    for _, row in edited_df.iterrows():
        key = stock_key(product_name, row["Material"], row["Specification"], row["Unit"])
        st.session_state.stock_values[key] = float(row.get("Stock Available", 0) or 0)

def final_df(product_name, quantity):
    df = stock_input_df(product_name, quantity)
    if df.empty:
        return df

    df["Stock Available"] = pd.to_numeric(df["Stock Available"], errors="coerce").fillna(0)
    df["Total Required"] = pd.to_numeric(df["Total Required"], errors="coerce").fillna(0)

    df["Order Quantity"] = (df["Total Required"] - df["Stock Available"]).clip(lower=0)
    df["Balance After Production"] = df["Stock Available"] - df["Total Required"]
    df["Status"] = df["Order Quantity"].apply(lambda x: "Enough Stock" if x == 0 else "Order Required")
    return df

def final_display_df(df):
    if df.empty:
        return df

    display = df.copy()
    for col in ["Required for 1 Piece", "Total Required", "Stock Available", "Order Quantity", "Balance After Production"]:
        display[col] = [format_qty(v, u) for v, u in zip(display[col], display["Unit"])]

    return display[[
        "Material",
        "Specification",
        "Unit",
        "Required for 1 Piece",
        "Total Required",
        "Stock Available",
        "Order Quantity",
        "Balance After Production",
        "Status",
    ]]

def download_csv(df, product_name, quantity):
    export = df.copy()
    export.insert(0, "Product", product_name)
    export.insert(1, "Production Quantity", quantity)
    export.insert(2, "Generated At", datetime.now().strftime("%Y-%m-%d %H:%M"))
    return export.to_csv(index=False).encode("utf-8")

def product_catalogue_df():
    rows = []
    for name, data in PRODUCTS.items():
        rows.append({
            "Product": name,
            "Category": data["category"],
            "Status": data["status"],
            "Component Lines": len(data["components"]),
        })
    return pd.DataFrame(rows)

# -----------------------------
# STYLE
# -----------------------------

st.markdown("""
<style>
    .block-container {
        max-width: 1180px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .top-card {
        background: #ffffff;
        border: 1px solid #e1e7ef;
        border-radius: 18px;
        padding: 24px 28px;
        margin-bottom: 18px;
        box-shadow: 0 8px 22px rgba(20, 35, 60, 0.05);
    }

    .brand {
        color: #1f4e8c;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .main-title {
        color: #172033;
        font-size: 2.35rem;
        line-height: 1.08;
        font-weight: 850;
        letter-spacing: -0.04em;
        margin: 0;
    }

    .subtitle {
        color: #5b677a;
        font-size: 1.03rem;
        margin-top: 8px;
    }

    .panel {
        background: #ffffff;
        border: 1px solid #e1e7ef;
        border-radius: 18px;
        padding: 20px 22px;
        margin-bottom: 18px;
        box-shadow: 0 8px 22px rgba(20, 35, 60, 0.04);
    }

    .step-label {
        color: #1f4e8c;
        font-size: 0.82rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 3px;
    }

    .panel-title {
        color: #172033;
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .panel-help {
        color: #5b677a;
        font-size: 0.98rem;
        margin-bottom: 14px;
    }

    .warning {
        background: #fff8e8;
        border: 1px solid #efc36b;
        color: #5c3b00;
        border-radius: 14px;
        padding: 14px 16px;
        margin: 12px 0 16px 0;
        font-size: 1rem;
    }

    .pending-box {
        background: #fff8e8;
        border: 1px solid #efc36b;
        color: #5c3b00;
        border-radius: 14px;
        padding: 18px 20px;
        margin-top: 14px;
        font-size: 1rem;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e1e7ef;
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 6px 16px rgba(20, 35, 60, 0.04);
    }

    .stDownloadButton > button {
        background: #1f4e8c !important;
        color: white !important;
        border: 1px solid #1f4e8c !important;
        border-radius: 12px !important;
        font-weight: 750 !important;
        height: 45px;
    }

    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
    }

    .footer {
        color: #6b7280;
        font-size: 0.88rem;
        text-align: center;
        margin-top: 22px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------

st.sidebar.title("ECL Planner")
st.sidebar.caption("Material Requirement Workflow")

page = st.sidebar.radio(
    "Pages",
    [
        "1. Required Components",
        "2. Stock Entry",
        "3. Final Summary",
        "Product List",
    ],
)

st.sidebar.divider()
st.sidebar.write("**Workflow**")
st.sidebar.write("1. Check required components")
st.sidebar.write("2. Enter available stock")
st.sidebar.write("3. Download final requirement")

# -----------------------------
# HEADER
# -----------------------------

st.markdown("""
<div class="top-card">
    <div class="brand">ECL India • Internal Factory Tool</div>
    <div class="main-title">Material Requirement Planner</div>
    <div class="subtitle">
        A simple three-step tool for checking production material, entering stock, and preparing the final order requirement.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# COMMON SELECTION PANEL
# -----------------------------

if page != "Product List":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Production selection</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-help">Select the product and quantity. The same selection is used across all three steps.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.7, 1])
    with c1:
        st.session_state.selected_product = st.selectbox(
            "Product / Model",
            list(PRODUCTS.keys()),
            index=list(PRODUCTS.keys()).index(st.session_state.selected_product),
        )
        selected_info = PRODUCTS[st.session_state.selected_product]
        st.caption(f"{selected_info['category']} • {selected_info['description']}")
    with c2:
        st.session_state.production_quantity = st.number_input(
            "How many finished pieces to make?",
            min_value=0,
            value=int(st.session_state.production_quantity),
            step=1,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    selected_product = st.session_state.selected_product
    quantity = st.session_state.production_quantity
    product_info = PRODUCTS[selected_product]

    if not product_has_bom(selected_product):
        st.markdown(
            f"""
            <div class="pending-box">
                <b>{selected_product}</b><br>
                Component list is <b>to be updated soon</b>. Upload or enter the internal BOM/material sheet before calculating this product.
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------
# PAGE 1: REQUIRED COMPONENTS
# -----------------------------

if page == "1. Required Components":
    if product_has_bom(selected_product):
        df = required_df(selected_product, quantity)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="step-label">Step 1</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Components required for production</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-help">This page shows the full material required before checking stock. You can download this list for stores or purchase planning.</div>',
            unsafe_allow_html=True,
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Product", selected_product)
        m2.metric("Production Quantity", f"{quantity:,.0f}")
        m3.metric("Component Lines", len(df))

        st.dataframe(required_display_df(df), use_container_width=True, hide_index=True)

        st.download_button(
            "Download Required Components",
            data=download_csv(df, selected_product, quantity),
            file_name=f"{selected_product.replace(' ', '_')}_required_components.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# PAGE 2: STOCK ENTRY
# -----------------------------

elif page == "2. Stock Entry":
    if product_has_bom(selected_product):
        df = stock_input_df(selected_product, quantity)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="step-label">Step 2</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Enter stock available</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-help">Enter what you currently have in stock. It is completely okay to keep stock as 0 if you do not know or do not want to enter it.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="warning"><b>Important:</b> Keep stock as 0 if you do not want to enter it. The app will still calculate the full requirement. For wire, enter stock in millimetres. Example: 500 metres = 500000 mm.</div>',
            unsafe_allow_html=True,
        )

        edited = st.data_editor(
            df,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=["Material", "Specification", "Unit", "Required for 1 Piece", "Total Required"],
            column_order=["Material", "Specification", "Unit", "Required for 1 Piece", "Total Required", "Stock Available"],
            column_config={
                "Material": st.column_config.TextColumn("Material", width="medium"),
                "Specification": st.column_config.TextColumn("Specification", width="large"),
                "Unit": st.column_config.TextColumn("Unit", width="small"),
                "Required for 1 Piece": st.column_config.NumberColumn("Required for 1", width="small"),
                "Total Required": st.column_config.NumberColumn("Total Required", width="medium"),
                "Stock Available": st.column_config.NumberColumn("Stock Available", min_value=0, step=1, width="medium"),
            },
            key=f"stock_editor_{selected_product}_{quantity}",
        )

        save_stock(selected_product, edited)

        st.success("Stock values saved for this session. Go to Step 3 to see the final requirement.")
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# PAGE 3: FINAL SUMMARY
# -----------------------------

elif page == "3. Final Summary":
    if product_has_bom(selected_product):
        df = final_df(selected_product, quantity)

        enough = int((df["Order Quantity"] == 0).sum())
        order_required = int((df["Order Quantity"] > 0).sum())
        pcs_to_order = df[df["Unit"] == "pcs"]["Order Quantity"].sum()
        wire_to_order_mm = df[df["Unit"] == "mm"]["Order Quantity"].sum()

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="step-label">Step 3</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Final business requirement</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="panel-help">This page compares required material against available stock and shows what must be ordered.</div>',
            unsafe_allow_html=True,
        )

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Enough Stock", enough)
        s2.metric("Need Order", order_required)
        s3.metric("Parts To Order", f"{pcs_to_order:,.0f} pcs")
        s4.metric("Wire To Order", f"{wire_to_order_mm / 1000:,.2f} m")

        final_table = final_display_df(df)

        def style_status(row):
            styles = [""] * len(row)
            if row["Status"] == "Order Required":
                styles[row.index.get_loc("Status")] = "background-color:#fff1e6;color:#9a3412;font-weight:800;"
                styles[row.index.get_loc("Order Quantity")] = "color:#9a3412;font-weight:800;"
            else:
                styles[row.index.get_loc("Status")] = "background-color:#eaf7ee;color:#166534;font-weight:800;"
            return styles

        st.dataframe(final_table.style.apply(style_status, axis=1), use_container_width=True, hide_index=True)

        st.download_button(
            "Download Final Summary File",
            data=download_csv(df, selected_product, quantity),
            file_name=f"{selected_product.replace(' ', '_')}_final_business_requirement.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# PRODUCT LIST
# -----------------------------

elif page == "Product List":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">ECL Product List</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="panel-help">Products with full material data can be calculated now. Other products are marked to be updated soon until their component list is provided.</div>',
        unsafe_allow_html=True,
    )

    cat_df = product_catalogue_df()
    ready_count = int((cat_df["Status"] == "READY").sum())
    pending_count = int((cat_df["Status"] != "READY").sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Products", len(cat_df))
    c2.metric("Ready", ready_count)
    c3.metric("To Be Updated", pending_count)

    st.dataframe(cat_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="footer">ECL India Material Requirement Planner • Internal factory use</div>', unsafe_allow_html=True)
