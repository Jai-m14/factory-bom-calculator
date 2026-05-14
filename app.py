import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(
    page_title="ECL Material Calculator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Minimal, safe CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Page wrapper */
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* Header card */
.ecl-header {
    background: #1F4E8C;
    color: #ffffff;
    border-radius: 10px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.6rem;
}
.ecl-header h1 { margin: 0 0 0.3rem 0; font-size: 1.8rem; font-weight: 700; }
.ecl-header p  { margin: 0; font-size: 1rem; opacity: 0.9; }

/* Step label */
.step-label {
    background: #1F4E8C;
    color: #fff;
    display: inline-block;
    border-radius: 20px;
    padding: 0.2rem 0.85rem;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

/* Warning box */
.warn-box {
    background: #FFF8E1;
    border-left: 4px solid #F59E0B;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    font-size: 0.92rem;
    margin-bottom: 1rem;
}

/* Summary cards */
.summary-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.4rem; }
.sum-card {
    flex: 1 1 160px;
    background: #fff;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    text-align: center;
}
.sum-card .sc-num  { font-size: 2rem; font-weight: 700; }
.sum-card .sc-lbl  { font-size: 0.82rem; color: #64748B; margin-top: 0.2rem; }
.sum-green .sc-num { color: #16A34A; }
.sum-orange .sc-num{ color: #EA580C; }
.sum-blue .sc-num  { color: #1F4E8C; }

/* Download button */
.stDownloadButton > button {
    background: #1F4E8C !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.4rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
}
.stDownloadButton > button:hover { background: #17407A !important; }

/* Collapsed future section */
details summary { cursor: pointer; color: #64748B; font-size: 0.88rem; }
details p, details ul { font-size: 0.88rem; color: #475569; }
</style>
""", unsafe_allow_html=True)


# ── Product data ───────────────────────────────────────────────────────────────
PRODUCTS = {
    "SHINE NEW": {
        "description": "New Shine stator wire harness",
        "materials": [
            {"Material": "White Coupler",             "Specification": "White connector / coupler",      "Unit": "pcs", "Needed for 1": 1},
            {"Material": "Terminal F Lock 6.4",       "Specification": "6.4 mm female lock terminal",    "Unit": "pcs", "Needed for 1": 2},
            {"Material": "Terminal CB104 Bullet",     "Specification": "CB104 bullet terminal",          "Unit": "pcs", "Needed for 1": 1},
            {"Material": "Cup Blue CB104",            "Specification": "Blue CB104 cup/cap",             "Unit": "pcs", "Needed for 1": 1},
            {"Material": "Black Grommet",             "Specification": "Black grommet",                  "Unit": "pcs", "Needed for 1": 1},
            {"Material": "Black PVC Sleeve",          "Specification": "150 mm, size 6 × 7",             "Unit": "pcs", "Needed for 1": 1},
            {"Material": "Yellow Silicone Sleeve",    "Specification": "5 mm sleeve, 70 mm length",      "Unit": "pcs", "Needed for 1": 1},
            {"Material": "PVC Wire 2×16/38 Green",    "Specification": "470 mm per harness",             "Unit": "mm",  "Needed for 1": 470},
            {"Material": "PVC Wire Green",            "Specification": "300 mm per harness",             "Unit": "mm",  "Needed for 1": 300},
            {"Material": "Blue Wire with Yellow Line","Specification": "300 mm per harness",             "Unit": "mm",  "Needed for 1": 300},
            {"Material": "White Wire",                "Specification": "360 mm per harness",             "Unit": "mm",  "Needed for 1": 360},
        ]
    },
    "SHINE OLD": {
        "description": "Old Shine stator wire harness",
        "materials": [
            {"Material": "White Coupler",             "Specification": "White connector / coupler",      "Unit": "pcs", "Needed for 1": 1},
            {"Material": "Terminal F Lock",           "Specification": "F Lock terminal",                "Unit": "pcs", "Needed for 1": 2},
            {"Material": "Terminal CB104 Bullet",     "Specification": "CB104 bullet terminal",          "Unit": "pcs", "Needed for 1": 1},
            {"Material": "Black Cap",                 "Specification": "Black cap",                      "Unit": "pcs", "Needed for 1": 1},
            {"Material": "Black Grommet",             "Specification": "Black grommet",                  "Unit": "pcs", "Needed for 1": 1},
            {"Material": "Black PVC Sleeve",          "Specification": "150 mm, size 6 × 7",             "Unit": "pcs", "Needed for 1": 1},
            {"Material": "Yellow Silicone Sleeve",    "Specification": "5 mm sleeve, 70 mm length",      "Unit": "pcs", "Needed for 1": 1},
            {"Material": "PVC Wire 2×16/38 Green",    "Specification": "330 mm per harness",             "Unit": "mm",  "Needed for 1": 330},
            {"Material": "PVC Wire Green",            "Specification": "550 mm per harness",             "Unit": "mm",  "Needed for 1": 550},
            {"Material": "Blue Wire with Yellow Line","Specification": "325 mm per harness",             "Unit": "mm",  "Needed for 1": 325},
            {"Material": "White Wire",                "Specification": "550 mm per harness",             "Unit": "mm",  "Needed for 1": 550},
        ]
    }
}

FUTURE_PRODUCTS = [
    "Horns DC", "Horns AC", "Stators", "Source Coils", "Light Coils",
    "Ignition Coils", "Igniters", "CDI Units", "Regulator Rectifiers",
    "Starter Relays", "Flashers", "Buzzers"
]


# ── Helper: mm display ─────────────────────────────────────────────────────────
def mm_display(val_mm):
    """Return a readable string for wire quantities: '470000 mm / 470 m'"""
    m = val_mm / 1000
    if m == int(m):
        return f"{int(val_mm):,} mm / {int(m):,} m"
    return f"{int(val_mm):,} mm / {m:.2f} m"


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ecl-header">
    <h1>🏭 ECL Material Calculator</h1>
    <p>Enter how many pieces to make. Enter stock if you know it. The app tells you what to order.</p>
</div>
""", unsafe_allow_html=True)

# ── Step 1 ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 1 — Select product and quantity</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    product_name = st.selectbox("Select product", list(PRODUCTS.keys()), label_visibility="visible")
with col2:
    qty = st.number_input("How many pieces to make?", min_value=0, value=1000, step=1)

st.caption(f"📋 {PRODUCTS[product_name]['description']}")
st.divider()

# ── Step 2 ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 2 — Enter stock available (leave blank if you don\'t know)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="warn-box">
⚠️ <strong>Unit reminder:</strong> For parts, enter pieces (pcs). 
For wire, enter millimetres (mm). Example: 500 metres = 500,000 mm.
</div>
""", unsafe_allow_html=True)

materials = PRODUCTS[product_name]["materials"]

# Build editor dataframe
editor_rows = []
for m in materials:
    total = m["Needed for 1"] * qty
    display_total = mm_display(total) if m["Unit"] == "mm" else f"{total:,} pcs"
    editor_rows.append({
        "Material": m["Material"],
        "Specification": m["Specification"],
        "Unit": m["Unit"],
        "Needed for 1": f"{m['Needed for 1']:,} {m['Unit']}",
        "Total Needed": display_total,
        "Stock Available": 0,
    })

editor_df = pd.DataFrame(editor_rows)

edited = st.data_editor(
    editor_df,
    use_container_width=True,
    hide_index=True,
    disabled=["Material", "Specification", "Unit", "Needed for 1", "Total Needed"],
    column_config={
        "Stock Available": st.column_config.NumberColumn(
            "Stock Available",
            help="Enter how much stock you currently have. Leave as 0 if unknown.",
            min_value=0,
            step=1,
            format="%d",
        )
    },
    key=f"editor_{product_name}"
)

st.divider()

# ── Step 3 — Calculate ─────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 3 — Order summary</div>', unsafe_allow_html=True)

result_rows = []
for i, m in enumerate(materials):
    total_needed = m["Needed for 1"] * qty
    stock = int(edited.iloc[i]["Stock Available"] or 0)
    order_qty = max(0, total_needed - stock)
    balance = stock - total_needed

    if m["Unit"] == "mm":
        total_disp   = mm_display(total_needed)
        order_disp   = mm_display(order_qty) if order_qty > 0 else f"0 mm / 0 m"
        balance_disp = (f"-{mm_display(-balance)}" if balance < 0
                        else f"{mm_display(balance)}" if balance > 0
                        else "0 mm / 0 m")
        stock_disp   = mm_display(stock) if stock > 0 else "0 mm / 0 m"
    else:
        total_disp   = f"{total_needed:,} pcs"
        order_disp   = f"{order_qty:,} pcs"
        balance_disp = f"{balance:,} pcs"
        stock_disp   = f"{stock:,} pcs"

    status = "✅ Enough" if order_qty == 0 else "🔴 Order"

    result_rows.append({
        "Material":            m["Material"],
        "Specification":       m["Specification"],
        "Unit":                m["Unit"],
        "Needed for 1":        f"{m['Needed for 1']:,} {m['Unit']}",
        "Total Needed":        total_disp,
        "Stock Available":     stock_disp,
        "Order Quantity":      order_disp,
        "Balance After Making":balance_disp,
        "Status":              status,
        # raw numerics for summary cards
        "_order_raw":          order_qty,
        "_unit":               m["Unit"],
    })

result_df = pd.DataFrame(result_rows)

# Summary counts
n_enough      = sum(1 for r in result_rows if r["_order_raw"] == 0)
n_order       = sum(1 for r in result_rows if r["_order_raw"] > 0)
n_parts_order = sum(1 for r in result_rows if r["_order_raw"] > 0 and r["_unit"] == "pcs")
n_wire_order  = sum(1 for r in result_rows if r["_order_raw"] > 0 and r["_unit"] == "mm")

st.markdown(f"""
<div class="summary-row">
  <div class="sum-card sum-green">
    <div class="sc-num">{n_enough}</div>
    <div class="sc-lbl">Enough Stock</div>
  </div>
  <div class="sum-card sum-orange">
    <div class="sc-num">{n_order}</div>
    <div class="sc-lbl">Need Order</div>
  </div>
  <div class="sum-card sum-blue">
    <div class="sc-num">{n_parts_order}</div>
    <div class="sc-lbl">Parts To Order</div>
  </div>
  <div class="sum-card sum-blue">
    <div class="sc-num">{n_wire_order}</div>
    <div class="sc-lbl">Wire To Order</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Display table (drop internal columns)
display_df = result_df.drop(columns=["_order_raw", "_unit"])

def colour_status(val):
    if "Enough" in str(val):
        return "background-color: #DCFCE7; color: #15803D; font-weight: 600;"
    elif "Order" in str(val):
        return "background-color: #FFEDD5; color: #C2410C; font-weight: 600;"
    return ""

styled = display_df.style.map(colour_status, subset=["Status"])
st.dataframe(styled, use_container_width=True, hide_index=True)

# ── CSV Export ─────────────────────────────────────────────────────────────────
csv_rows = []
for r in result_rows:
    csv_rows.append({
        "Product":               product_name,
        "Production Quantity":   qty,
        "Generated At":          datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Material":              r["Material"],
        "Specification":         r["Specification"],
        "Unit":                  r["Unit"],
        "Needed for 1":          r["Needed for 1"],
        "Total Needed":          r["Total Needed"],
        "Stock Available":       r["Stock Available"],
        "Order Quantity":        r["Order Quantity"],
        "Balance After Making":  r["Balance After Making"],
        "Status":                r["Status"].replace("✅ ", "").replace("🔴 ", ""),
    })

csv_df = pd.DataFrame(csv_rows)
csv_buf = io.StringIO()
csv_df.to_csv(csv_buf, index=False)
csv_bytes = csv_buf.getvalue().encode("utf-8")

filename = f"ECL_Order_{product_name.replace(' ', '_')}_{qty}pcs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

st.download_button(
    label="⬇️ Download Order Sheet (CSV)",
    data=csv_bytes,
    file_name=filename,
    mime="text/csv",
)

# ── Future products section ────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
future_list = "\n".join(f"<li>{p}</li>" for p in FUTURE_PRODUCTS)
st.markdown(f"""
<details>
<summary>📁 For office use: other ECL products to add later</summary>
<p>Only <strong>SHINE NEW</strong> and <strong>SHINE OLD</strong> have full material data right now.
Add more products when their material sheets are available.</p>
<p><strong>Future product families:</strong></p>
<ul>{future_list}</ul>
</details>
""", unsafe_allow_html=True)
