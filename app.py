
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="ECL Material Planner",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

DEFAULT_PRODUCTS = {
    "SHINE NEW": {
        "category": "Stators / Wire Harness",
        "description": "Wire Shine Stator harness - new model using Cup Blue CB104.",
        "components": [
            {"Component Name": "White Coupler", "Specification": "White connector / coupler", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "Terminal F Lock 6.4", "Specification": "6.4 mm female lock terminal", "Unit": "pcs", "Required Per Unit": 2.0},
            {"Component Name": "Terminal CB104 Bullet", "Specification": "CB104 bullet terminal", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "Cup Blue CB104", "Specification": "Blue CB104 cup/cap", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "Black Grommet", "Specification": "Black grommet", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "Black PVC Sleeve", "Specification": "150 mm, size 6 × 7", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "Yellow Silicone Sleeve", "Specification": "5 mm sleeve, 70 mm length", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "PVC Wire 2×16/38 Green", "Specification": "470 mm per harness", "Unit": "mm", "Required Per Unit": 470.0},
            {"Component Name": "PVC Wire Green", "Specification": "300 mm per harness", "Unit": "mm", "Required Per Unit": 300.0},
            {"Component Name": "Blue Wire with Yellow Line", "Specification": "300 mm per harness", "Unit": "mm", "Required Per Unit": 300.0},
            {"Component Name": "White Wire", "Specification": "360 mm per harness", "Unit": "mm", "Required Per Unit": 360.0},
        ],
    },
    "SHINE OLD": {
        "category": "Stators / Wire Harness",
        "description": "Wire Shine Stator harness - old model using Black Cap.",
        "components": [
            {"Component Name": "White Coupler", "Specification": "White connector / coupler", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "Terminal F Lock", "Specification": "F Lock terminal", "Unit": "pcs", "Required Per Unit": 2.0},
            {"Component Name": "Terminal CB104 Bullet", "Specification": "CB104 bullet terminal", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "Black Cap", "Specification": "Black cap", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "Black Grommet", "Specification": "Black grommet", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "Black PVC Sleeve", "Specification": "150 mm, size 6 × 7", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "Yellow Silicone Sleeve", "Specification": "5 mm sleeve, 70 mm length", "Unit": "pcs", "Required Per Unit": 1.0},
            {"Component Name": "PVC Wire 2×16/38 Green", "Specification": "330 mm per harness", "Unit": "mm", "Required Per Unit": 330.0},
            {"Component Name": "PVC Wire Green", "Specification": "550 mm per harness", "Unit": "mm", "Required Per Unit": 550.0},
            {"Component Name": "Blue Wire with Yellow Line", "Specification": "325 mm per harness", "Unit": "mm", "Required Per Unit": 325.0},
            {"Component Name": "White Wire", "Specification": "550 mm per harness", "Unit": "mm", "Required Per Unit": 550.0},
        ],
    },
}

ECL_CATALOGUE = [
    ("Horns DC - Windtone Black", "Horns DC"),
    ("Horns DC - Windtone", "Horns DC"),
    ("Horns DC - 2W", "Horns DC"),
    ("Horns DC - 2W HD", "Horns DC"),
    ("Horns AC - 2W 6V & 12V Flower Type", "Horns AC"),
    ("Horns AC - 2W 6V & 12V Milano Type", "Horns AC"),
    ("Horns AC - 2W 6V & 12V Super XL", "Horns AC"),
    ("Stators - 2W", "Stators"),
    ("Source Coils - 2W", "Source Coils"),
    ("Light Coils - 2W", "Light Coils"),
    ("Ignition Coils - 2W", "Ignition Coils"),
    ("Igniters - 2W", "Igniters"),
    ("CDI Units - 2W CT 100", "CDI Units"),
    ("Regulator Rectifiers - 2W", "Regulator Rectifiers"),
    ("Starter Relays - 2W Old Model", "Starter Relays"),
    ("Starter Relays - 2W 12V", "Starter Relays"),
    ("Flashers - 2W", "Flashers"),
    ("Buzzers - 2W", "Buzzers"),
]

ALLOWED_UNITS = ["pcs", "mm", "m", "kg", "g", "litre", "ml"]

def init_state():
    if "products" not in st.session_state:
        products = {k: v.copy() for k, v in DEFAULT_PRODUCTS.items()}
        for product_name, category in ECL_CATALOGUE:
            if product_name not in products:
                products[product_name] = {
                    "category": category,
                    "description": "Catalogue item. Add internal BOM before calculation.",
                    "components": [],
                }
        st.session_state.products = products

    if "stock_store" not in st.session_state:
        st.session_state.stock_store = {}

init_state()

def component_key(row):
    return f"{row['Component Name']}|{row['Specification']}|{row['Unit']}"

def format_quantity(value, unit):
    value = float(value or 0)
    if unit == "pcs":
        return f"{value:,.0f} pcs"
    if unit == "mm":
        return f"{value:,.0f} mm ({value / 1000:,.2f} m)"
    return f"{value:,.2f} {unit}"

def get_product_df(product_name):
    product = st.session_state.products[product_name]
    df = pd.DataFrame(product["components"])
    if df.empty:
        return pd.DataFrame(columns=["Component Name", "Specification", "Unit", "Required Per Unit", "Stock In Hand"])
    df["Required Per Unit"] = pd.to_numeric(df["Required Per Unit"], errors="coerce").fillna(0)
    df["Stock In Hand"] = [float(st.session_state.stock_store.get(component_key(row), 0) or 0) for _, row in df.iterrows()]
    return df

def save_stock_from_df(df):
    for _, row in df.iterrows():
        st.session_state.stock_store[component_key(row)] = float(row.get("Stock In Hand", 0) or 0)

def calculate(df, quantity, wastage):
    if df.empty:
        return df
    result = df.copy()
    result["Required Per Unit"] = pd.to_numeric(result["Required Per Unit"], errors="coerce").fillna(0)
    result["Stock In Hand"] = pd.to_numeric(result["Stock In Hand"], errors="coerce").fillna(0)
    result["Total Needed"] = result["Required Per Unit"] * quantity
    material_mask = result["Unit"].isin(["mm", "m", "kg", "g", "litre", "ml"])
    result.loc[material_mask, "Total Needed"] *= (1 + wastage / 100)
    result["Quantity To Order"] = (result["Total Needed"] - result["Stock In Hand"]).clip(lower=0)
    result["Balance After Production"] = result["Stock In Hand"] - result["Total Needed"]
    result["Status"] = result["Quantity To Order"].apply(lambda x: "Enough Stock" if x <= 0 else "Order Required")
    return result

def format_table(result):
    table = result.copy()
    for col in ["Required Per Unit", "Total Needed", "Stock In Hand", "Quantity To Order", "Balance After Production"]:
        table[col] = [format_quantity(v, u) for v, u in zip(table[col], table["Unit"])]
    return table[[
        "Component Name", "Specification", "Unit", "Required Per Unit",
        "Total Needed", "Stock In Hand", "Quantity To Order",
        "Balance After Production", "Status"
    ]]

def build_csv(result, product_name, quantity):
    export = result.copy()
    export.insert(0, "Product / Model", product_name)
    export.insert(1, "Production Quantity", quantity)
    export.insert(2, "Generated At", datetime.now().strftime("%Y-%m-%d %H:%M"))
    return export.to_csv(index=False).encode("utf-8")

st.markdown("""
<style>
    .stApp {
        background: #f4f6f9;
        color: #172033;
    }

    .block-container {
        max-width: 1240px;
        padding-top: 1.25rem;
        padding-bottom: 3rem;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #dde3ec;
    }

    section[data-testid="stSidebar"] * {
        color: #172033 !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: #172033;
    }

    .hero {
        background: #ffffff;
        border: 1px solid #dde3ec;
        border-left: 8px solid #1f4e8c;
        border-radius: 18px;
        padding: 26px 30px;
        margin-bottom: 20px;
        box-shadow: 0 8px 22px rgba(22, 34, 51, 0.06);
    }

    .brand-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }

    .brand {
        color: #1f4e8c;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero-title {
        color: #172033;
        font-size: 2.35rem;
        line-height: 1.08;
        font-weight: 850;
        letter-spacing: -0.04em;
        margin: 0;
    }

    .hero-subtitle {
        color: #526071;
        font-size: 1.04rem;
        margin-top: 10px;
        max-width: 820px;
    }

    .ecl-pill {
        border: 1px solid #c9d8ee;
        background: #eff6ff;
        color: #1f4e8c;
        padding: 8px 13px;
        border-radius: 999px;
        font-weight: 750;
        white-space: nowrap;
    }

    .panel {
        background: #ffffff;
        border: 1px solid #dde3ec;
        border-radius: 18px;
        padding: 20px 22px;
        margin-bottom: 18px;
        box-shadow: 0 8px 22px rgba(22, 34, 51, 0.05);
    }

    .panel-title {
        color: #172033;
        font-weight: 850;
        font-size: 1.28rem;
        margin-bottom: 2px;
    }

    .panel-help {
        color: #637083;
        font-size: 0.96rem;
        margin-bottom: 15px;
    }

    .notice {
        background: #fff8eb;
        border: 1px solid #f0c56b;
        color: #7a4b00;
        padding: 13px 15px;
        border-radius: 13px;
        margin: 12px 0 16px 0;
        font-size: 0.96rem;
    }

    .notice b {
        color: #5c3800;
    }

    .ready-badge {
        display: inline-block;
        border-radius: 999px;
        background: #eaf7ee;
        color: #166534;
        border: 1px solid #bce2c6;
        font-size: 0.78rem;
        font-weight: 800;
        padding: 6px 10px;
    }

    .pending-badge {
        display: inline-block;
        border-radius: 999px;
        background: #fff4e6;
        color: #9a3412;
        border: 1px solid #fdc68a;
        font-size: 0.78rem;
        font-weight: 800;
        padding: 6px 10px;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dde3ec;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 6px 18px rgba(22, 34, 51, 0.05);
    }

    div[data-testid="stMetricLabel"] p {
        color: #637083 !important;
        font-weight: 650;
    }

    div[data-testid="stMetricValue"] {
        color: #172033;
        font-weight: 850;
    }

    .stButton > button, .stDownloadButton > button {
        background: #1f4e8c !important;
        color: #ffffff !important;
        border: 1px solid #1f4e8c !important;
        border-radius: 12px !important;
        font-weight: 750 !important;
        min-height: 42px;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #173d70 !important;
        color: #ffffff !important;
        border: 1px solid #173d70 !important;
    }

    div[data-baseweb="select"] * {
        color: #172033 !important;
    }

    input {
        color: #172033 !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #dde3ec;
        border-radius: 14px;
        overflow: hidden;
    }

    .small-note {
        color: #637083;
        font-size: 0.88rem;
        margin-top: 6px;
    }

    .footer {
        color: #637083;
        text-align: center;
        padding: 16px;
        font-size: 0.86rem;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("### ECL Material Planner")
st.sidebar.caption("Internal production planning")
page = st.sidebar.radio("Menu", ["Production Calculator", "BOM Manager", "Product Catalogue"])
st.sidebar.divider()
st.sidebar.caption("Simple flow")
st.sidebar.write("Select product → enter quantity → enter stock → download order sheet")

st.markdown("""
<div class="hero">
    <div class="brand-row">
        <div>
            <div class="brand">ECL India • Internal Factory Tool</div>
            <div class="hero-title">Material Requirement Planner</div>
            <div class="hero-subtitle">
                Calculate required material, compare available stock, and prepare a purchase order sheet for production.
            </div>
        </div>
        <div class="ecl-pill">BOM Calculator</div>
    </div>
</div>
""", unsafe_allow_html=True)

if page == "Production Calculator":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Production setup</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-help">Select the product and production quantity. Stock entry is optional; blank stock is treated as zero.</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([1.7, 1, 1, 0.8])
    with col1:
        selected_product = st.selectbox("Product / Model", list(st.session_state.products.keys()))
    with col2:
        quantity = st.number_input("Production Quantity", min_value=0, value=1000, step=1)
    with col3:
        wastage = st.number_input("Wastage %", min_value=0.0, value=0.0, step=0.5)
    with col4:
        product = st.session_state.products[selected_product]
        st.write("BOM Status")
        badge = '<span class="ready-badge">READY</span>' if product["components"] else '<span class="pending-badge">PENDING</span>'
        st.markdown(badge, unsafe_allow_html=True)

    st.markdown(f'<div class="small-note">{product.get("category", "")} • {product.get("description", "")}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not product["components"]:
        st.warning("This ECL catalogue item is saved as a placeholder. Add its internal BOM in BOM Manager before calculation.")
        st.stop()

    df = get_product_df(selected_product)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Stock entry</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-help">Only the Stock In Hand column is editable. BOM quantities are locked to avoid mistakes.</div>', unsafe_allow_html=True)
    st.markdown('<div class="notice"><b>Unit rule:</b> Enter stock in the same unit shown. For wire in mm, enter millimetres. Example: 500 metres = 500000 mm.</div>', unsafe_allow_html=True)

    edited = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["Component Name", "Specification", "Unit", "Required Per Unit"],
        column_config={
            "Component Name": st.column_config.TextColumn("Material Name", width="medium"),
            "Specification": st.column_config.TextColumn("Specification", width="large"),
            "Unit": st.column_config.TextColumn("Unit", width="small"),
            "Required Per Unit": st.column_config.NumberColumn("Required / Unit", format="%.2f"),
            "Stock In Hand": st.column_config.NumberColumn("Stock In Hand", min_value=0, step=1, format="%.2f"),
        },
        key=f"stock_editor_{selected_product}",
    )
    save_stock_from_df(edited)
    st.markdown("</div>", unsafe_allow_html=True)

    result = calculate(edited, quantity, wastage)

    enough = int((result["Status"] == "Enough Stock").sum())
    shortage = int((result["Status"] == "Order Required").sum())
    pieces_to_order = result[result["Unit"] == "pcs"]["Quantity To Order"].sum()
    wire_to_order = result[result["Unit"] == "mm"]["Quantity To Order"].sum()

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("BOM Lines", len(result))
    s2.metric("Enough Stock", enough)
    s3.metric("Need Order", shortage)
    s4.metric("Pieces To Order", f"{pieces_to_order:,.0f}")
    s5.metric("Wire To Order", f"{wire_to_order / 1000:,.2f} m")

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Final order sheet</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-help">Use this table for purchase planning or stores verification.</div>', unsafe_allow_html=True)

    final_table = format_table(result)

    def style_status(row):
        styles = [""] * len(row)
        if row["Status"] == "Order Required":
            styles[row.index.get_loc("Status")] = "background-color:#fff4e6;color:#9a3412;font-weight:800;"
            styles[row.index.get_loc("Quantity To Order")] = "color:#9a3412;font-weight:800;"
        else:
            styles[row.index.get_loc("Status")] = "background-color:#eaf7ee;color:#166534;font-weight:800;"
        return styles

    st.dataframe(final_table.style.apply(style_status, axis=1), use_container_width=True, hide_index=True)

    st.download_button(
        "Download Order Sheet CSV",
        data=build_csv(result, selected_product, quantity),
        file_name=f"{selected_product.replace(' ', '_').replace('/', '-')}_order_sheet.csv",
        mime="text/csv",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "BOM Manager":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">BOM Manager</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-help">Add or edit material requirements for future ECL products. Keep this section for office/admin use.</div>', unsafe_allow_html=True)

    selected = st.selectbox("Product to edit", list(st.session_state.products.keys()))
    product = st.session_state.products[selected]

    c1, c2 = st.columns([1, 2])
    with c1:
        product["category"] = st.text_input("Category", value=product.get("category", "Uncategorised"))
    with c2:
        product["description"] = st.text_input("Description", value=product.get("description", ""))

    st.subheader("Current BOM")
    if product["components"]:
        bom_df = pd.DataFrame(product["components"])
        edited_bom = st.data_editor(
            bom_df,
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Unit": st.column_config.SelectboxColumn("Unit", options=ALLOWED_UNITS),
                "Required Per Unit": st.column_config.NumberColumn("Required Per Unit", min_value=0, step=1),
            },
            key=f"bom_{selected}"
        )
        product["components"] = edited_bom.to_dict("records")
    else:
        st.info("No BOM added yet for this product.")

    st.subheader("Add component")
    a1, a2, a3, a4 = st.columns([1.3, 2, 0.7, 1])
    with a1:
        name = st.text_input("Component Name")
    with a2:
        spec = st.text_input("Specification")
    with a3:
        unit = st.selectbox("Unit", ALLOWED_UNITS)
    with a4:
        req = st.number_input("Required / Unit", min_value=0.0, value=1.0, step=1.0)

    if st.button("Add Component", use_container_width=True):
        if not name.strip():
            st.error("Component name is required.")
        else:
            product["components"].append({
                "Component Name": name.strip(),
                "Specification": spec.strip(),
                "Unit": unit,
                "Required Per Unit": float(req),
            })
            st.success("Component added.")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Product Catalogue":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">ECL Product Catalogue</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-help">Products with BOM READY can be calculated. BOM PENDING products need internal material data first.</div>', unsafe_allow_html=True)

    rows = []
    for name, data in st.session_state.products.items():
        rows.append({
            "Product / Model": name,
            "Category": data.get("category", "Uncategorised"),
            "BOM Status": "BOM READY" if data.get("components") else "BOM PENDING",
            "Material Lines": len(data.get("components", [])),
            "Description": data.get("description", ""),
        })
    catalogue = pd.DataFrame(rows).sort_values(["Category", "Product / Model"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Products", len(catalogue))
    c2.metric("BOM Ready", int((catalogue["BOM Status"] == "BOM READY").sum()))
    c3.metric("BOM Pending", int((catalogue["BOM Status"] == "BOM PENDING").sum()))

    st.dataframe(catalogue, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="footer">ECL India internal material planning tool</div>', unsafe_allow_html=True)
