import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(
    page_title="ECL Material Calculator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Minimal, safe CSS based on the approved baseline ──────────────────────────
st.markdown("""
<style>
.block-container { padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1180px; }

.ecl-header {
    background: #1F4E8C;
    color: #ffffff;
    border-radius: 10px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.3rem;
}
.ecl-header h1 { margin: 0 0 0.3rem 0; font-size: 1.85rem; font-weight: 700; color: #ffffff; }
.ecl-header p  { margin: 0; font-size: 1rem; opacity: 0.92; color: #ffffff; }

.step-label {
    background: #1F4E8C;
    color: #fff;
    display: inline-block;
    border-radius: 20px;
    padding: 0.2rem 0.85rem;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 0.55rem;
}

.info-card {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1rem 1.15rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.warn-box {
    background: #FFF8E1;
    border-left: 4px solid #F59E0B;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    font-size: 0.92rem;
    margin-bottom: 1rem;
}

.pending-box {
    background: #FFF8E1;
    border-left: 4px solid #F59E0B;
    border-radius: 6px;
    padding: 1rem 1.1rem;
    font-size: 0.96rem;
    margin: 1rem 0;
}

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

.small-note { color: #64748B; font-size: 0.9rem; margin-top: 0.25rem; }
</style>
""", unsafe_allow_html=True)

# ── Product data ───────────────────────────────────────────────────────────────
PRODUCTS = {
    "SHINE NEW": {
        "category": "Stators / Wire Harness",
        "status": "READY",
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
        "category": "Stators / Wire Harness",
        "status": "READY",
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
    },
}

# Public product placeholders until component lists are provided.
for _name, _cat in [
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
]:
    PRODUCTS.setdefault(_name, {
        "category": _cat,
        "status": "TO BE UPDATED SOON",
        "description": "Component list to be updated soon",
        "materials": []
    })

# ── State ─────────────────────────────────────────────────────────────────────
if "product_name" not in st.session_state:
    st.session_state.product_name = "SHINE NEW"
if "qty" not in st.session_state:
    st.session_state.qty = 1000
if "stock" not in st.session_state:
    st.session_state.stock = {}

# ── Helpers ───────────────────────────────────────────────────────────────────
def mm_display(val_mm):
    val_mm = float(val_mm or 0)
    m = val_mm / 1000
    if m == int(m):
        return f"{int(val_mm):,} mm / {int(m):,} m"
    return f"{int(val_mm):,} mm / {m:.2f} m"

def qty_display(value, unit):
    if unit == "mm":
        return mm_display(value)
    return f"{int(float(value or 0)):,} pcs"

def stock_id(product, material, spec, unit):
    return f"{product}|{material}|{spec}|{unit}"

def has_materials(product):
    return len(PRODUCTS[product]["materials"]) > 0

def required_rows(product, qty):
    rows = []
    for m in PRODUCTS[product]["materials"]:
        total = m["Needed for 1"] * qty
        rows.append({
            "Material": m["Material"],
            "Specification": m["Specification"],
            "Unit": m["Unit"],
            "Needed for 1": m["Needed for 1"],
            "Total Required": total,
        })
    return rows

def required_display(product, qty):
    rows = []
    for r in required_rows(product, qty):
        rows.append({
            "Material": r["Material"],
            "Specification": r["Specification"],
            "Unit": r["Unit"],
            "Needed for 1": qty_display(r["Needed for 1"], r["Unit"]),
            "Total Required": qty_display(r["Total Required"], r["Unit"]),
        })
    return pd.DataFrame(rows)

def stock_editor_df(product, qty):
    rows = []
    for r in required_rows(product, qty):
        key = stock_id(product, r["Material"], r["Specification"], r["Unit"])
        rows.append({
            "Material": r["Material"],
            "Specification": r["Specification"],
            "Unit": r["Unit"],
            "Needed for 1": qty_display(r["Needed for 1"], r["Unit"]),
            "Total Required": qty_display(r["Total Required"], r["Unit"]),
            "Stock Available": int(st.session_state.stock.get(key, 0) or 0),
        })
    return pd.DataFrame(rows)

def save_stock_from_editor(product, edited_df):
    for _, row in edited_df.iterrows():
        key = stock_id(product, row["Material"], row["Specification"], row["Unit"])
        st.session_state.stock[key] = int(row.get("Stock Available", 0) or 0)

def final_raw(product, qty):
    rows = []
    for m in PRODUCTS[product]["materials"]:
        total_needed = int(m["Needed for 1"] * qty)
        key = stock_id(product, m["Material"], m["Specification"], m["Unit"])
        stock = int(st.session_state.stock.get(key, 0) or 0)
        order_qty = max(0, total_needed - stock)
        balance = stock - total_needed
        rows.append({
            "Material": m["Material"],
            "Specification": m["Specification"],
            "Unit": m["Unit"],
            "Needed for 1": m["Needed for 1"],
            "Total Required": total_needed,
            "Stock Available": stock,
            "Order Quantity": order_qty,
            "Balance After Making": balance,
            "Status": "Enough Stock" if order_qty == 0 else "Order Required",
        })
    return pd.DataFrame(rows)

def final_display(df):
    rows = []
    for _, r in df.iterrows():
        unit = r["Unit"]
        balance = r["Balance After Making"]
        if unit == "mm" and balance < 0:
            bal_disp = "-" + mm_display(abs(balance))
        else:
            bal_disp = qty_display(balance, unit)
        rows.append({
            "Material": r["Material"],
            "Specification": r["Specification"],
            "Unit": unit,
            "Needed for 1": qty_display(r["Needed for 1"], unit),
            "Total Required": qty_display(r["Total Required"], unit),
            "Stock Available": qty_display(r["Stock Available"], unit),
            "Order Quantity": qty_display(r["Order Quantity"], unit),
            "Balance After Making": bal_disp,
            "Status": r["Status"],
        })
    return pd.DataFrame(rows)

def csv_bytes(df, product, qty):
    export = df.copy()
    export.insert(0, "Product", product)
    export.insert(1, "Production Quantity", qty)
    export.insert(2, "Generated At", datetime.now().strftime("%Y-%m-%d %H:%M"))
    buf = io.StringIO()
    export.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")

def page_selection_panel():
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.35, 1])
    with col1:
        st.session_state.product_name = st.selectbox(
            "Select product",
            list(PRODUCTS.keys()),
            index=list(PRODUCTS.keys()).index(st.session_state.product_name),
        )
    with col2:
        st.session_state.qty = st.number_input(
            "How many pieces to make?",
            min_value=0,
            value=int(st.session_state.qty),
            step=1,
        )
    info = PRODUCTS[st.session_state.product_name]
    st.caption(f"📋 {info['category']} • {info['description']}")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ecl-header">
    <h1>🏭 ECL Material Calculator</h1>
    <p>Three-step production material planner: required components, stock entry, and final business requirement.</p>
</div>
""", unsafe_allow_html=True)

# ── Navigation ─────────────────────────────────────────────────────────────────
st.sidebar.title("ECL Planner")
st.sidebar.caption("Internal factory workflow")
page = st.sidebar.radio(
    "Go to page",
    ["1. Required Components", "2. Stock Entry", "3. Final Summary", "Product List"],
)
st.sidebar.divider()
st.sidebar.write("**Workflow**")
st.sidebar.write("1. See required components")
st.sidebar.write("2. Enter available stock")
st.sidebar.write("3. Download final summary")

# ── Product List ───────────────────────────────────────────────────────────────
if page == "Product List":
    st.markdown('<div class="step-label">Product List</div>', unsafe_allow_html=True)
    st.write("Products without component lists are marked **TO BE UPDATED SOON** until you provide the material sheet.")
    cat_rows = []
    for name, data in PRODUCTS.items():
        cat_rows.append({
            "Product": name,
            "Category": data["category"],
            "Status": data["status"],
            "Component Lines": len(data["materials"]),
        })
    cat_df = pd.DataFrame(cat_rows)
    ready = int((cat_df["Status"] == "READY").sum())
    pending = len(cat_df) - ready
    st.markdown(f"""
    <div class="summary-row">
      <div class="sum-card sum-blue"><div class="sc-num">{len(cat_df)}</div><div class="sc-lbl">Total Products</div></div>
      <div class="sum-card sum-green"><div class="sc-num">{ready}</div><div class="sc-lbl">Ready</div></div>
      <div class="sum-card sum-orange"><div class="sc-num">{pending}</div><div class="sc-lbl">To Be Updated</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(cat_df, use_container_width=True, hide_index=True)
    st.stop()

# Common selection on the 3 workflow pages
page_selection_panel()
product_name = st.session_state.product_name
qty = st.session_state.qty

if not has_materials(product_name):
    st.markdown(f"""
    <div class="pending-box">
    <strong>{product_name}</strong><br>
    Component list is <strong>TO BE UPDATED SOON</strong>. Upload/provide the material sheet for this product before calculation.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Page 1: Required Components ────────────────────────────────────────────────
if page == "1. Required Components":
    st.markdown('<div class="step-label">Step 1 — Required components</div>', unsafe_allow_html=True)
    st.write("This page shows everything required for the selected production quantity before checking stock.")

    req_df = required_display(product_name, qty)
    raw_req = pd.DataFrame(required_rows(product_name, qty))

    wire_total = raw_req.loc[raw_req["Unit"] == "mm", "Total Required"].sum()
    part_lines = int((raw_req["Unit"] == "pcs").sum())
    wire_lines = int((raw_req["Unit"] == "mm").sum())

    st.markdown(f"""
    <div class="summary-row">
      <div class="sum-card sum-blue"><div class="sc-num">{qty:,}</div><div class="sc-lbl">Pieces To Make</div></div>
      <div class="sum-card sum-blue"><div class="sc-num">{len(req_df)}</div><div class="sc-lbl">Component Lines</div></div>
      <div class="sum-card sum-blue"><div class="sc-num">{part_lines}</div><div class="sc-lbl">Part Lines</div></div>
      <div class="sum-card sum-blue"><div class="sc-num">{wire_total/1000:,.2f} m</div><div class="sc-lbl">Total Wire Required</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(req_df, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download Required Components",
        data=csv_bytes(raw_req, product_name, qty),
        file_name=f"ECL_Required_Components_{product_name.replace(' ', '_')}_{qty}pcs.csv",
        mime="text/csv",
    )

# ── Page 2: Stock Entry ───────────────────────────────────────────────────────
elif page == "2. Stock Entry":
    st.markdown('<div class="step-label">Step 2 — Enter stock available</div>', unsafe_allow_html=True)
    st.write("Enter how much material you currently have. It is okay to keep stock as **0** if you do not want to enter it.")
    st.markdown("""
    <div class="warn-box">
    ⚠️ <strong>Important:</strong> Keep stock as <strong>0</strong> if you do not know it. The app will still calculate the full requirement.
    For parts, enter pieces. For wire, enter millimetres. Example: 500 metres = 500,000 mm.
    </div>
    """, unsafe_allow_html=True)

    edf = stock_editor_df(product_name, qty)
    edited = st.data_editor(
        edf,
        use_container_width=True,
        hide_index=True,
        disabled=["Material", "Specification", "Unit", "Needed for 1", "Total Required"],
        column_config={
            "Stock Available": st.column_config.NumberColumn(
                "Stock Available",
                help="Enter current stock. Keep as 0 if unknown or not entered.",
                min_value=0,
                step=1,
                format="%d",
            )
        },
        key=f"stock_editor_{product_name}_{qty}",
    )
    save_stock_from_editor(product_name, edited)
    st.success("Stock values saved for this session. Go to Step 3 to see the final business requirement.")

# ── Page 3: Final Summary ─────────────────────────────────────────────────────
elif page == "3. Final Summary":
    st.markdown('<div class="step-label">Step 3 — Final business requirement</div>', unsafe_allow_html=True)
    st.write("This page compares required material with available stock and shows what needs to be ordered.")

    raw = final_raw(product_name, qty)
    display = final_display(raw)

    n_enough = int((raw["Order Quantity"] == 0).sum())
    n_order = int((raw["Order Quantity"] > 0).sum())
    pieces_to_order = raw.loc[raw["Unit"] == "pcs", "Order Quantity"].sum()
    wire_to_order = raw.loc[raw["Unit"] == "mm", "Order Quantity"].sum()

    st.markdown(f"""
    <div class="summary-row">
      <div class="sum-card sum-green"><div class="sc-num">{n_enough}</div><div class="sc-lbl">Enough Stock</div></div>
      <div class="sum-card sum-orange"><div class="sc-num">{n_order}</div><div class="sc-lbl">Need Order</div></div>
      <div class="sum-card sum-blue"><div class="sc-num">{int(pieces_to_order):,}</div><div class="sc-lbl">Parts To Order</div></div>
      <div class="sum-card sum-blue"><div class="sc-num">{wire_to_order/1000:,.2f} m</div><div class="sc-lbl">Wire To Order</div></div>
    </div>
    """, unsafe_allow_html=True)

    def colour_status(val):
        if "Enough" in str(val):
            return "background-color: #DCFCE7; color: #15803D; font-weight: 600;"
        if "Order" in str(val):
            return "background-color: #FFEDD5; color: #C2410C; font-weight: 600;"
        return ""

    styled = display.style.map(colour_status, subset=["Status"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download Final Summary File",
        data=csv_bytes(raw, product_name, qty),
        file_name=f"ECL_Final_Summary_{product_name.replace(' ', '_')}_{qty}pcs.csv",
        mime="text/csv",
    )
