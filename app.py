
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Factory Material Calculator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

PRODUCTS = {
    "SHINE NEW": {
        "category": "Wire Harness",
        "description": "New model harness using Cup Blue CB104.",
        "components": [
            ["White Coupler", "White connector / coupler", "pcs", 1],
            ["Terminal F Lock 6.4", "6.4 mm female lock terminal", "pcs", 2],
            ["Terminal CB104 Bullet", "CB104 bullet terminal", "pcs", 1],
            ["Cup Blue CB104", "Blue CB104 cup/cap", "pcs", 1],
            ["Black Grommet", "Black grommet", "pcs", 1],
            ["Black PVC Sleeve", "150 mm, size 6 × 7", "pcs", 1],
            ["Yellow Silicone Sleeve", "5 mm sleeve, 70 mm length", "pcs", 1],
            ["PVC Wire 2×16/38 Green", "470 mm per harness", "mm", 470],
            ["PVC Wire Green", "300 mm per harness", "mm", 300],
            ["Blue Wire with Yellow Line", "300 mm per harness", "mm", 300],
            ["White Wire", "360 mm per harness", "mm", 360],
        ],
    },
    "SHINE OLD": {
        "category": "Wire Harness",
        "description": "Old model harness using Black Cap.",
        "components": [
            ["White Coupler", "White connector / coupler", "pcs", 1],
            ["Terminal F Lock", "F Lock terminal", "pcs", 2],
            ["Terminal CB104 Bullet", "CB104 bullet terminal", "pcs", 1],
            ["Black Cap", "Black cap", "pcs", 1],
            ["Black Grommet", "Black grommet", "pcs", 1],
            ["Black PVC Sleeve", "150 mm, size 6 × 7", "pcs", 1],
            ["Yellow Silicone Sleeve", "5 mm sleeve, 70 mm length", "pcs", 1],
            ["PVC Wire 2×16/38 Green", "330 mm per harness", "mm", 330],
            ["PVC Wire Green", "550 mm per harness", "mm", 550],
            ["Blue Wire with Yellow Line", "325 mm per harness", "mm", 325],
            ["White Wire", "550 mm per harness", "mm", 550],
        ],
    },
}

CATALOGUE_PENDING = [
    "Horns DC - Windtone Black",
    "Horns DC - Windtone",
    "Horns DC - 2W",
    "Horns AC - 2W 6V & 12V Flower Type",
    "Horns AC - 2W 6V & 12V Milano Type",
    "Horns AC - 2W 6V & 12V Super XL",
    "Stators - 2W",
    "Source Coils - 2W",
    "Light Coils - 2W",
    "Ignition Coils - 2W",
    "Igniters - 2W",
    "CDI Units - 2W CT 100",
    "Regulator Rectifiers - 2W",
    "Starter Relays - 2W Old Model",
    "Starter Relays - 2W 12V",
    "Flashers - 2W",
    "Buzzers - 2W",
]

def format_qty(value, unit):
    value = float(value or 0)
    if unit == "mm":
        return f"{value:,.0f} mm ({value/1000:,.2f} m)"
    if unit == "pcs":
        return f"{value:,.0f} pcs"
    return f"{value:,.2f} {unit}"

def make_base_df(product_name):
    product = PRODUCTS[product_name]
    df = pd.DataFrame(product["components"], columns=[
        "Material Name", "Specification", "Unit", "Needed Per Harness"
    ])
    df["Stock In Hand"] = 0.0
    return df

def calculate(df, production_qty, wastage_percent):
    result = df.copy()
    result["Needed Per Harness"] = pd.to_numeric(result["Needed Per Harness"], errors="coerce").fillna(0)
    result["Stock In Hand"] = pd.to_numeric(result["Stock In Hand"], errors="coerce").fillna(0)

    result["Total Needed"] = result["Needed Per Harness"] * production_qty
    wire_mask = result["Unit"].eq("mm")
    result.loc[wire_mask, "Total Needed"] = result.loc[wire_mask, "Total Needed"] * (1 + wastage_percent / 100)

    result["Quantity To Order"] = (result["Total Needed"] - result["Stock In Hand"]).clip(lower=0)
    result["Balance After Making"] = result["Stock In Hand"] - result["Total Needed"]
    result["Status"] = result["Quantity To Order"].apply(lambda x: "Enough Stock" if x <= 0 else "Order Required")
    return result

def display_df(result):
    shown = result.copy()
    for col in ["Needed Per Harness", "Total Needed", "Stock In Hand", "Quantity To Order", "Balance After Making"]:
        shown[col] = [format_qty(v, u) for v, u in zip(shown[col], shown["Unit"])]
    return shown

def csv_bytes(result, product_name, production_qty):
    out = result.copy()
    out.insert(0, "Product", product_name)
    out.insert(1, "Production Quantity", production_qty)
    return out.to_csv(index=False).encode("utf-8")

st.markdown("""
<style>
    .stApp {
        background: #f6f1e8;
    }
    h1 {
        font-size: 2.4rem !important;
        letter-spacing: -0.03em;
    }
    h2, h3 {
        letter-spacing: -0.02em;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e6ded0;
        border-radius: 18px;
        padding: 18px;
    }
    .simple-card {
        background: white;
        border: 1px solid #e6ded0;
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 18px;
    }
    .notice {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #7c2d12;
        padding: 14px 16px;
        border-radius: 16px;
        font-size: 1.05rem;
        margin: 12px 0 18px 0;
    }
    .ok {
        color: #15803d;
        font-weight: 700;
    }
    .bad {
        color: #c2410c;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Factory Material Calculator")
st.write("Simple order calculator for factory production. Select the product, enter quantity, enter available stock, and download the order sheet.")

with st.container():
    st.markdown('<div class="simple-card">', unsafe_allow_html=True)
    st.subheader("1. Production details")

    c1, c2, c3 = st.columns([1.4, 1, 1])
    with c1:
        product_name = st.selectbox("Product / Model", list(PRODUCTS.keys()))
        st.caption(PRODUCTS[product_name]["description"])
    with c2:
        production_qty = st.number_input("Pieces to make", min_value=0, value=1000, step=1)
    with c3:
        wastage_percent = st.number_input("Wire wastage %", min_value=0.0, value=0.0, step=0.5)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="notice"><b>Rule:</b> Enter component stock in pieces. Enter wire stock in millimetres. '
    'Example: 500 metres = 500000 mm. If stock is blank, it is treated as 0.</div>',
    unsafe_allow_html=True
)

base_df = make_base_df(product_name)

st.markdown('<div class="simple-card">', unsafe_allow_html=True)
st.subheader("2. Enter stock in hand")
st.write("Only edit the **Stock In Hand** column. Leave it as 0 if you do not know current stock.")

edited_df = st.data_editor(
    base_df,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "Material Name": st.column_config.TextColumn("Material Name", disabled=True),
        "Specification": st.column_config.TextColumn("Specification", disabled=True),
        "Unit": st.column_config.TextColumn("Unit", disabled=True),
        "Needed Per Harness": st.column_config.NumberColumn("Needed Per Harness", disabled=True),
        "Stock In Hand": st.column_config.NumberColumn("Stock In Hand", min_value=0, step=1),
    },
    disabled=["Material Name", "Specification", "Unit", "Needed Per Harness"],
    key=f"stock_editor_{product_name}",
)
st.markdown("</div>", unsafe_allow_html=True)

result = calculate(edited_df, production_qty, wastage_percent)

enough_lines = int((result["Status"] == "Enough Stock").sum())
order_lines = int((result["Status"] == "Order Required").sum())
pieces_to_order = result[result["Unit"].eq("pcs")]["Quantity To Order"].sum()
wire_to_order_mm = result[result["Unit"].eq("mm")]["Quantity To Order"].sum()

st.subheader("3. Result summary")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Enough Stock", enough_lines)
m2.metric("Need Order", order_lines)
m3.metric("Pieces To Order", f"{pieces_to_order:,.0f} pcs")
m4.metric("Wire To Order", f"{wire_to_order_mm/1000:,.2f} m")

st.markdown('<div class="simple-card">', unsafe_allow_html=True)
st.subheader("4. Final order sheet")
st.dataframe(display_df(result), use_container_width=True, hide_index=True)

st.download_button(
    "⬇️ Download Order Sheet",
    data=csv_bytes(result, product_name, production_qty),
    file_name=f"{product_name.replace(' ', '_')}_order_sheet.csv",
    mime="text/csv",
    use_container_width=True
)
st.markdown("</div>", unsafe_allow_html=True)

with st.expander("Products to add later"):
    st.write("These are company product families/placeholders. Add BOM sheets later before calculating them.")
    pending_df = pd.DataFrame({"Product / Family": CATALOGUE_PENDING, "BOM Status": "Pending"})
    st.dataframe(pending_df, use_container_width=True, hide_index=True)

with st.expander("Admin note: how to add more products"):
    st.write(
        "For now, add a new product by copying the SHINE NEW structure inside app.py and replacing the material rows. "
        "This keeps the main screen simple for parents and staff. A full add/edit screen can be added later once the calculator workflow is confirmed."
    )
