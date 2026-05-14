
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="ECL Factory Material Planner",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# DATA
# -----------------------------

DEFAULT_PRODUCTS = {
    "SHINE NEW": {
        "category": "Stators / Wire Harness",
        "status": "BOM READY",
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
        "status": "BOM READY",
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

# -----------------------------
# STATE
# -----------------------------

def init_state():
    if "products" not in st.session_state:
        products = {k: v.copy() for k, v in DEFAULT_PRODUCTS.items()}
        for product_name, category in ECL_CATALOGUE:
            if product_name not in products:
                products[product_name] = {
                    "category": category,
                    "status": "BOM PENDING",
                    "description": "Public ECL product family. Add internal BOM before calculating.",
                    "components": [],
                }
        st.session_state.products = products

    if "stock_store" not in st.session_state:
        st.session_state.stock_store = {}

init_state()

# -----------------------------
# HELPERS
# -----------------------------

def component_key(row):
    return f"{row['Component Name']}|{row['Specification']}|{row['Unit']}"

def format_quantity(value, unit):
    value = float(value or 0)
    if unit == "pcs":
        return f"{value:,.0f} pcs"
    if unit == "mm":
        return f"{value:,.0f} mm ({value / 1000:,.2f} m)"
    if unit == "m":
        return f"{value:,.2f} m"
    if unit in ["kg", "g", "litre", "ml"]:
        return f"{value:,.2f} {unit}"
    return f"{value:,.2f} {unit}"

def get_product_df(product_name):
    product = st.session_state.products[product_name]
    df = pd.DataFrame(product["components"])
    if df.empty:
        return pd.DataFrame(columns=["Component Name", "Specification", "Unit", "Required Per Unit", "Stock In Hand"])
    df["Required Per Unit"] = pd.to_numeric(df["Required Per Unit"], errors="coerce").fillna(0)
    stock_values = []
    for _, row in df.iterrows():
        stock_values.append(float(st.session_state.stock_store.get(component_key(row), 0) or 0))
    df["Stock In Hand"] = stock_values
    return df

def calculate(df, production_qty, wastage_percent):
    if df.empty:
        return df
    result = df.copy()
    result["Required Per Unit"] = pd.to_numeric(result["Required Per Unit"], errors="coerce").fillna(0)
    result["Stock In Hand"] = pd.to_numeric(result["Stock In Hand"], errors="coerce").fillna(0)
    result["Total Needed"] = result["Required Per Unit"] * production_qty

    wastage_units = result["Unit"].isin(["mm", "m", "kg", "g", "litre", "ml"])
    result.loc[wastage_units, "Total Needed"] = result.loc[wastage_units, "Total Needed"] * (1 + wastage_percent / 100)

    result["Quantity To Order"] = (result["Total Needed"] - result["Stock In Hand"]).clip(lower=0)
    result["Balance After Production"] = result["Stock In Hand"] - result["Total Needed"]
    result["Status"] = result["Quantity To Order"].apply(lambda x: "Enough Stock" if x <= 0 else "Order Required")
    return result

def format_result_table(result):
    shown = result.copy()
    for col in ["Required Per Unit", "Stock In Hand", "Total Needed", "Quantity To Order", "Balance After Production"]:
        shown[col] = [format_quantity(v, u) for v, u in zip(shown[col], shown["Unit"])]
    shown = shown[[
        "Component Name", "Specification", "Unit", "Required Per Unit",
        "Total Needed", "Stock In Hand", "Quantity To Order",
        "Balance After Production", "Status"
    ]]
    return shown

def build_csv(result, product_name, production_qty):
    export = result.copy()
    export.insert(0, "Product / Model", product_name)
    export.insert(1, "Production Quantity", production_qty)
    export.insert(2, "Generated At", datetime.now().strftime("%Y-%m-%d %H:%M"))
    return export.to_csv(index=False).encode("utf-8")

def save_stock_from_df(df):
    for _, row in df.iterrows():
        key = component_key(row)
        st.session_state.stock_store[key] = float(row.get("Stock In Hand", 0) or 0)

# -----------------------------
# CSS
# -----------------------------

st.markdown("""
<style>
    :root {
        --ecl-navy: #101828;
        --ecl-blue: #1d4ed8;
        --ecl-light: #f5f7fb;
        --ecl-border: #e5e7eb;
        --ecl-green: #15803d;
        --ecl-orange: #c2410c;
    }

    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
        color: var(--ecl-navy);
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    section[data-testid="stSidebar"] {
        background: #0f172a;
    }

    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    .ecl-hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #2563eb 100%);
        border-radius: 24px;
        padding: 30px 34px;
        color: white;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
        margin-bottom: 22px;
    }

    .ecl-hero h1 {
        margin: 0;
        font-size: 2.55rem;
        letter-spacing: -0.04em;
        line-height: 1.05;
    }

    .ecl-hero p {
        margin: 10px 0 0 0;
        color: #dbeafe;
        font-size: 1.05rem;
        max-width: 820px;
    }

    .ecl-badge {
        display: inline-block;
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.28);
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .panel {
        background: white;
        border: 1px solid var(--ecl-border);
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 10px 28px rgba(15,23,42,0.06);
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
        color: #101828;
    }

    .section-help {
        color: #667085;
        margin-bottom: 18px;
        font-size: 0.98rem;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--ecl-border);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 22px rgba(15,23,42,0.05);
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 800;
    }

    .warning-box {
        background: #fff7ed;
        border: 1px solid #fdba74;
        color: #7c2d12;
        padding: 14px 16px;
        border-radius: 16px;
        margin: 12px 0 16px 0;
        font-size: 0.98rem;
    }

    .ready {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #dcfce7;
        color: #166534;
        font-weight: 800;
        font-size: 0.78rem;
    }

    .pending {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #ffedd5;
        color: #9a3412;
        font-weight: 800;
        font-size: 0.78rem;
    }

    .footer-note {
        color: #64748b;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 28px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.markdown("## ECL Planner")
st.sidebar.caption("Internal material planning tool")
page = st.sidebar.radio(
    "Navigation",
    ["Production Calculator", "BOM Manager", "Product Catalogue"],
    label_visibility="collapsed"
)

st.sidebar.divider()
st.sidebar.caption("Workflow")
st.sidebar.write("1. Select product")
st.sidebar.write("2. Enter quantity")
st.sidebar.write("3. Enter stock")
st.sidebar.write("4. Download order sheet")

# -----------------------------
# HEADER
# -----------------------------

st.markdown("""
<div class="ecl-hero">
    <div class="ecl-badge">ECL Magtronics • Internal Tool</div>
    <h1>Factory Material Requirement Planner</h1>
    <p>Professional BOM calculator for production planning, stock checking and purchase order preparation.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# PAGES
# -----------------------------

if page == "Production Calculator":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Production setup</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-help">Choose the product and production quantity. Stock entry is optional. Blank stock is treated as zero.</div>', unsafe_allow_html=True)

    product_names = list(st.session_state.products.keys())
    ready_count = sum(1 for p in st.session_state.products.values() if len(p.get("components", [])) > 0)
    pending_count = len(product_names) - ready_count

    top1, top2, top3, top4 = st.columns([1.5, 1, 1, 1])
    with top1:
        selected_product = st.selectbox("Product / Model", product_names)
    with top2:
        production_qty = st.number_input("Production quantity", min_value=0, value=1000, step=1)
    with top3:
        wastage_percent = st.number_input("Wastage %", min_value=0.0, value=0.0, step=0.5)
    with top4:
        product = st.session_state.products[selected_product]
        status_html = '<span class="ready">BOM READY</span>' if product.get("components") else '<span class="pending">BOM PENDING</span>'
        st.markdown("**BOM Status**")
        st.markdown(status_html, unsafe_allow_html=True)

    st.caption(f"{product.get('category', 'Uncategorised')} • {product.get('description', '')}")
    st.markdown("</div>", unsafe_allow_html=True)

    if not product.get("components"):
        st.warning("This product is in the ECL catalogue, but its internal BOM has not been added yet. Add the BOM in BOM Manager before calculating material.")
        st.stop()

    df = get_product_df(selected_product)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Stock entry</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-help">Edit only the stock column. All BOM quantities are locked to prevent accidental changes.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="warning-box"><b>Unit rule:</b> Enter stock in the same unit shown. For wire in mm, enter millimetres. Example: 500 metres = 500000 mm.</div>',
        unsafe_allow_html=True
    )

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
        key=f"editor_{selected_product}",
    )
    save_stock_from_df(edited)
    st.markdown("</div>", unsafe_allow_html=True)

    result = calculate(edited, production_qty, wastage_percent)

    enough = int((result["Status"] == "Enough Stock").sum())
    order = int((result["Status"] == "Order Required").sum())
    pieces_to_order = result[result["Unit"] == "pcs"]["Quantity To Order"].sum()
    mm_to_order = result[result["Unit"] == "mm"]["Quantity To Order"].sum()
    total_lines = len(result)

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("BOM Lines", total_lines)
    s2.metric("Enough Stock", enough)
    s3.metric("Need Order", order)
    s4.metric("Pieces To Order", f"{pieces_to_order:,.0f}")
    s5.metric("Wire To Order", f"{mm_to_order / 1000:,.2f} m")

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Final order sheet</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-help">This is the purchase/stores view. Download it and send it to the concerned person.</div>', unsafe_allow_html=True)

    final_table = format_result_table(result)

    def highlight_status(row):
        if row["Status"] == "Order Required":
            return ["background-color: #fff7ed; color: #9a3412;" if col == "Status" else "" for col in row.index]
        return ["background-color: #f0fdf4; color: #166534;" if col == "Status" else "" for col in row.index]

    st.dataframe(
        final_table.style.apply(highlight_status, axis=1),
        use_container_width=True,
        hide_index=True
    )

    col_a, col_b = st.columns([1, 3])
    with col_a:
        st.download_button(
            "Download Order Sheet",
            data=build_csv(result, selected_product, production_qty),
            file_name=f"{selected_product.replace(' ', '_').replace('/', '-')}_order_sheet.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_b:
        st.caption("CSV includes product name, production quantity, stock, shortage, balance and status.")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "BOM Manager":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">BOM Manager</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-help">Use this section to add future ECL products and their material requirements. Keep this for office/admin use.</div>', unsafe_allow_html=True)

    selected = st.selectbox("Select product to edit", list(st.session_state.products.keys()))
    product = st.session_state.products[selected]

    c1, c2 = st.columns(2)
    with c1:
        product["category"] = st.text_input("Category", value=product.get("category", "Uncategorised"))
    with c2:
        product["description"] = st.text_input("Description", value=product.get("description", ""))

    st.markdown("### Add component")
    a1, a2, a3, a4 = st.columns([1.3, 2, 0.7, 1])
    with a1:
        new_component = st.text_input("Component Name")
    with a2:
        new_spec = st.text_input("Specification")
    with a3:
        new_unit = st.selectbox("Unit", ALLOWED_UNITS)
    with a4:
        new_required = st.number_input("Required / Unit", min_value=0.0, value=1.0, step=1.0)

    if st.button("Add Component", use_container_width=True):
        if not new_component.strip():
            st.error("Component name is required.")
        else:
            product["components"].append({
                "Component Name": new_component.strip(),
                "Specification": new_spec.strip(),
                "Unit": new_unit,
                "Required Per Unit": float(new_required),
            })
            product["status"] = "BOM READY"
            st.success("Component added.")

    st.markdown("### Current BOM")
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
            key=f"bom_manager_{selected}",
        )
        product["components"] = edited_bom.to_dict("records")
        product["status"] = "BOM READY" if len(product["components"]) else "BOM PENDING"
    else:
        st.info("No BOM components added yet for this product.")

    st.divider()
    st.markdown("### Add new product")
    n1, n2 = st.columns([1, 1])
    with n1:
        product_name = st.text_input("New Product Name")
    with n2:
        product_category = st.text_input("New Product Category", value="Uncategorised")

    if st.button("Create New Product"):
        if not product_name.strip():
            st.error("Enter product name.")
        elif product_name.strip() in st.session_state.products:
            st.error("Product already exists.")
        else:
            st.session_state.products[product_name.strip()] = {
                "category": product_category.strip() or "Uncategorised",
                "status": "BOM PENDING",
                "description": "New internal product. Add BOM components.",
                "components": [],
            }
            st.success("Product created.")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Product Catalogue":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ECL Product Catalogue</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-help">Public product families are preloaded as placeholders. Only products with internal BOMs can be calculated.</div>', unsafe_allow_html=True)

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

    ready = int((catalogue["BOM Status"] == "BOM READY").sum())
    pending = int((catalogue["BOM Status"] == "BOM PENDING").sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Products", len(catalogue))
    c2.metric("BOM Ready", ready)
    c3.metric("BOM Pending", pending)

    st.dataframe(catalogue, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="footer-note">ECL Magtronics internal planning tool • Built for material requirement calculation</div>', unsafe_allow_html=True)
