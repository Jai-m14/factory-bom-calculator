
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="ECL Material Calculator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

PRODUCTS = {
    "SHINE NEW": {
        "description": "New Shine stator wire harness",
        "items": [
            ("White Coupler", "White connector / coupler", "pcs", 1),
            ("Terminal F Lock 6.4", "6.4 mm female lock terminal", "pcs", 2),
            ("Terminal CB104 Bullet", "CB104 bullet terminal", "pcs", 1),
            ("Cup Blue CB104", "Blue CB104 cup/cap", "pcs", 1),
            ("Black Grommet", "Black grommet", "pcs", 1),
            ("Black PVC Sleeve", "150 mm, size 6 × 7", "pcs", 1),
            ("Yellow Silicone Sleeve", "5 mm sleeve, 70 mm length", "pcs", 1),
            ("PVC Wire 2×16/38 Green", "470 mm per harness", "mm", 470),
            ("PVC Wire Green", "300 mm per harness", "mm", 300),
            ("Blue Wire with Yellow Line", "300 mm per harness", "mm", 300),
            ("White Wire", "360 mm per harness", "mm", 360),
        ],
    },
    "SHINE OLD": {
        "description": "Old Shine stator wire harness",
        "items": [
            ("White Coupler", "White connector / coupler", "pcs", 1),
            ("Terminal F Lock", "F Lock terminal", "pcs", 2),
            ("Terminal CB104 Bullet", "CB104 bullet terminal", "pcs", 1),
            ("Black Cap", "Black cap", "pcs", 1),
            ("Black Grommet", "Black grommet", "pcs", 1),
            ("Black PVC Sleeve", "150 mm, size 6 × 7", "pcs", 1),
            ("Yellow Silicone Sleeve", "5 mm sleeve, 70 mm length", "pcs", 1),
            ("PVC Wire 2×16/38 Green", "330 mm per harness", "mm", 330),
            ("PVC Wire Green", "550 mm per harness", "mm", 550),
            ("Blue Wire with Yellow Line", "325 mm per harness", "mm", 325),
            ("White Wire", "550 mm per harness", "mm", 550),
        ],
    },
}

def qty_text(value, unit):
    value = float(value or 0)
    if unit == "pcs":
        return f"{value:,.0f} pcs"
    if unit == "mm":
        return f"{value:,.0f} mm  /  {value / 1000:,.2f} m"
    return f"{value:,.2f} {unit}"

def build_table(product_name, quantity):
    rows = []
    for name, spec, unit, per_piece in PRODUCTS[product_name]["items"]:
        needed = per_piece * quantity
        rows.append({
            "Material": name,
            "Specification": spec,
            "Unit": unit,
            "Needed for 1": per_piece,
            "Total Needed": needed,
            "Stock Available": 0.0,
        })
    return pd.DataFrame(rows)

def calculate_order(df):
    result = df.copy()
    result["Stock Available"] = pd.to_numeric(result["Stock Available"], errors="coerce").fillna(0)
    result["Total Needed"] = pd.to_numeric(result["Total Needed"], errors="coerce").fillna(0)

    result["Order Quantity"] = (result["Total Needed"] - result["Stock Available"]).clip(lower=0)
    result["Balance After Making"] = result["Stock Available"] - result["Total Needed"]
    result["Status"] = result["Order Quantity"].apply(lambda x: "Enough" if x == 0 else "Order")
    return result

def show_table(result):
    display = result.copy()
    for col in ["Needed for 1", "Total Needed", "Stock Available", "Order Quantity", "Balance After Making"]:
        display[col] = [qty_text(v, u) for v, u in zip(display[col], display["Unit"])]
    return display[[
        "Material",
        "Specification",
        "Unit",
        "Needed for 1",
        "Total Needed",
        "Stock Available",
        "Order Quantity",
        "Balance After Making",
        "Status",
    ]]

def csv_file(result, product, quantity):
    export = result.copy()
    export.insert(0, "Product", product)
    export.insert(1, "Production Quantity", quantity)
    export.insert(2, "Generated At", datetime.now().strftime("%Y-%m-%d %H:%M"))
    return export.to_csv(index=False).encode("utf-8")

st.markdown("""
<style>
    .block-container {
        max-width: 1100px;
        padding-top: 1.5rem;
    }

    .main-title {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 24px 28px;
        margin-bottom: 18px;
    }

    .main-title h1 {
        margin: 0;
        color: #172033;
        font-size: 2.2rem;
        letter-spacing: -0.03em;
    }

    .main-title p {
        margin: 8px 0 0 0;
        color: #5B677A;
        font-size: 1.05rem;
    }

    .box {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 20px 22px;
        margin-bottom: 18px;
    }

    .step {
        color: #1F4E8C;
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    .box-title {
        color: #172033;
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .help {
        color: #5B677A;
        margin-bottom: 14px;
    }

    .warning {
        background: #FFF7E6;
        border: 1px solid #F5C76B;
        color: #5A3A00;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 16px;
        font-size: 1rem;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 14px;
    }

    .stDownloadButton > button {
        background: #1F4E8C !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        height: 46px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-title">
    <h1>ECL Material Calculator</h1>
    <p>Enter how many pieces to make. Enter stock if you know it. The app tells you what to order.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="box">', unsafe_allow_html=True)
st.markdown('<div class="step">Step 1</div>', unsafe_allow_html=True)
st.markdown('<div class="box-title">Select product and quantity</div>', unsafe_allow_html=True)

c1, c2 = st.columns([1.4, 1])
with c1:
    product = st.selectbox("Product", list(PRODUCTS.keys()), label_visibility="visible")
    st.caption(PRODUCTS[product]["description"])
with c2:
    quantity = st.number_input("How many pieces to make?", min_value=0, value=1000, step=1)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="box">', unsafe_allow_html=True)
st.markdown('<div class="step">Step 2</div>', unsafe_allow_html=True)
st.markdown('<div class="box-title">Enter stock available</div>', unsafe_allow_html=True)
st.markdown('<div class="help">Only change the stock column. Leave it as 0 if you do not know current stock.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="warning"><b>Important:</b> For parts, enter pieces. For wire, enter millimetres. Example: 500 metres = 500000 mm.</div>',
    unsafe_allow_html=True
)

base_df = build_table(product, quantity)

edited = st.data_editor(
    base_df,
    hide_index=True,
    use_container_width=True,
    num_rows="fixed",
    disabled=["Material", "Specification", "Unit", "Needed for 1", "Total Needed"],
    column_order=["Material", "Specification", "Unit", "Needed for 1", "Total Needed", "Stock Available"],
    column_config={
        "Material": st.column_config.TextColumn("Material", width="medium"),
        "Specification": st.column_config.TextColumn("Specification", width="large"),
        "Unit": st.column_config.TextColumn("Unit", width="small"),
        "Needed for 1": st.column_config.NumberColumn("Needed for 1", width="small"),
        "Total Needed": st.column_config.NumberColumn("Total Needed", width="medium"),
        "Stock Available": st.column_config.NumberColumn("Stock Available", min_value=0, step=1, width="medium"),
    },
    key=f"stock_table_{product}_{quantity}",
)

st.markdown('</div>', unsafe_allow_html=True)

result = calculate_order(edited)

need_order = int((result["Order Quantity"] > 0).sum())
enough = int((result["Order Quantity"] == 0).sum())
parts_to_order = result[result["Unit"] == "pcs"]["Order Quantity"].sum()
wire_to_order_mm = result[result["Unit"] == "mm"]["Order Quantity"].sum()

st.markdown('<div class="box">', unsafe_allow_html=True)
st.markdown('<div class="step">Step 3</div>', unsafe_allow_html=True)
st.markdown('<div class="box-title">Final result</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Enough Stock", enough)
m2.metric("Need Order", need_order)
m3.metric("Parts To Order", f"{parts_to_order:,.0f} pcs")
m4.metric("Wire To Order", f"{wire_to_order_mm / 1000:,.2f} m")

final = show_table(result)

def status_style(row):
    styles = [""] * len(row)
    if row["Status"] == "Order":
        styles[row.index.get_loc("Status")] = "background-color:#FFF1E6;color:#9A3412;font-weight:800;"
        styles[row.index.get_loc("Order Quantity")] = "color:#9A3412;font-weight:800;"
    else:
        styles[row.index.get_loc("Status")] = "background-color:#EAF7EE;color:#166534;font-weight:800;"
    return styles

st.dataframe(final.style.apply(status_style, axis=1), use_container_width=True, hide_index=True)

st.download_button(
    "Download Order Sheet",
    data=csv_file(result, product, quantity),
    file_name=f"{product.replace(' ', '_')}_order_sheet.csv",
    mime="text/csv",
    use_container_width=True,
)

st.markdown('</div>', unsafe_allow_html=True)

with st.expander("For office use: other ECL products to add later"):
    st.write("Only SHINE NEW and SHINE OLD have full BOM data right now. Add more products when their BOM sheets are available.")
    st.write("Future product families: Horns DC, Horns AC, Stators, Source Coils, Light Coils, Ignition Coils, Igniters, CDI Units, Regulator Rectifiers, Starter Relays, Flashers and Buzzers.")
