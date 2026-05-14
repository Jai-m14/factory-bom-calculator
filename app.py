
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Factory BOM & Material Calculator",
    page_icon="🏭",
    layout="wide"
)

# Products with full BOM data from the Excel sheet provided.
DEFAULT_PRODUCTS = {
    "SHINE NEW": {
        "category": "Stators / Wire Harness",
        "description": "Full BOM available from uploaded Excel. New model wire harness using Cup Blue CB104.",
        "bom_status": "BOM READY",
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
        "description": "Full BOM available from uploaded Excel. Old model wire harness using Black Cap.",
        "bom_status": "BOM READY",
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

# Public product families and visible model placeholders from eclindia.in.
# These do not have BOMs yet. Add components when internal BOM sheets are available.
ECL_PUBLIC_CATALOG_TEMPLATES = {
    "HORNS DC - WINDTONE BLACK": {"category": "Horns DC", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},
    "HORNS DC - WINDTONE": {"category": "Horns DC", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},
    "HORNS DC - 2W": {"category": "Horns DC", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},
    "HORNS DC - 2W HD": {"category": "Horns DC", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},

    "HORNS AC - 2W 6V & 12V FLOWER TYPE": {"category": "Horns AC", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},
    "HORNS AC - 2W 6V & 12V MILANO TYPE": {"category": "Horns AC", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},
    "HORNS AC - 2W 6V & 12V SUPER XL": {"category": "Horns AC", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},

    "STATORS - 2W": {"category": "Stators", "description": "Public ECL product family. Add individual stator BOMs later.", "bom_status": "BOM PENDING", "components": []},
    "SOURCE COILS - 2W": {"category": "Source Coils", "description": "Public ECL product family. Add individual source coil BOMs later.", "bom_status": "BOM PENDING", "components": []},
    "LIGHT COILS - 2W": {"category": "Light Coils", "description": "Public ECL product family. Add individual light coil BOMs later.", "bom_status": "BOM PENDING", "components": []},

    "IGNITION COILS - 2W": {"category": "Ignition Coils", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},
    "IGNITERS - 2W": {"category": "Igniters", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},

    "CDI UNITS - 2W CT 100": {"category": "CDI Units", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},
    "REGULATOR RECTIFIERS - 2W": {"category": "Regulator Rectifiers", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},

    "STARTER RELAYS - 2W OLD MODEL": {"category": "Starter Relays", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},
    "STARTER RELAYS - 2W 12V": {"category": "Starter Relays", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},

    "FLASHERS - 2W": {"category": "Flashers", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},
    "BUZZERS - 2W": {"category": "Buzzers", "description": "Public ECL product listing. BOM not added yet.", "bom_status": "BOM PENDING", "components": []},
}

ALLOWED_UNITS = ["pcs", "mm", "m", "kg", "g", "litre", "ml"]

def initialize_state():
    if "products" not in st.session_state:
        st.session_state.products = {**DEFAULT_PRODUCTS, **ECL_PUBLIC_CATALOG_TEMPLATES}
    if "stock" not in st.session_state:
        st.session_state.stock = {}

def material_key(component):
    return f"{component['Component Name']}|{component['Specification']}|{component['Unit']}"

def format_qty(value, unit):
    value = 0 if pd.isna(value) else float(value)
    if unit == "mm":
        return f"{value:,.0f} mm ({value / 1000:,.2f} m)"
    if unit == "pcs":
        return f"{value:,.0f} pcs"
    return f"{value:,.2f} {unit}"

def calculate_requirements(product_name, production_qty, wastage_percent):
    product = st.session_state.products[product_name]
    rows = []
    for c in product["components"]:
        required_per_unit = float(c["Required Per Unit"])
        unit = c["Unit"]
        total_needed = required_per_unit * production_qty

        if unit in ["mm", "m", "kg", "g", "litre", "ml"]:
            total_needed *= (1 + wastage_percent / 100)

        key = material_key(c)
        stock_in_hand = float(st.session_state.stock.get(key, 0) or 0)
        order_qty = max(0, total_needed - stock_in_hand)
        balance = stock_in_hand - total_needed
        status = "Enough Stock" if order_qty == 0 else "Order Required"

        rows.append({
            "Component Name": c["Component Name"],
            "Specification": c["Specification"],
            "Unit": unit,
            "Required Per Unit": required_per_unit,
            "Total Needed": total_needed,
            "Stock In Hand": stock_in_hand,
            "Quantity To Order": order_qty,
            "Balance After Production": balance,
            "Status": status,
            "Stock Key": key
        })
    return pd.DataFrame(rows)

def make_csv(df, product_name, production_qty):
    export_df = df.drop(columns=["Stock Key"], errors="ignore").copy()
    export_df.insert(0, "Product / Model", product_name)
    export_df.insert(1, "Production Quantity", production_qty)
    return export_df.to_csv(index=False).encode("utf-8")

def apply_table_formatting(df):
    display_df = df.drop(columns=["Stock Key"], errors="ignore").copy()
    for col in ["Required Per Unit", "Total Needed", "Stock In Hand", "Quantity To Order", "Balance After Production"]:
        display_df[col] = [
            format_qty(value, unit) for value, unit in zip(display_df[col], display_df["Unit"])
        ]
    return display_df

initialize_state()

st.markdown("""
<style>
    .main { background-color: #f7f3ea; }
    h1, h2, h3 { color: #1f2937; }
    .stMetric { background: white; padding: 18px; border-radius: 14px; border: 1px solid #e5e7eb; }
    .warning-box {
        background-color: #fff7ed;
        border: 1px solid #fdba74;
        padding: 16px;
        border-radius: 14px;
        color: #7c2d12;
        font-size: 18px;
        margin-bottom: 18px;
    }
    .pending-box {
        background-color: #eff6ff;
        border: 1px solid #93c5fd;
        padding: 16px;
        border-radius: 14px;
        color: #1e3a8a;
        font-size: 18px;
        margin-bottom: 18px;
    }
    .success-text { color: #15803d; font-weight: 700; }
    .danger-text { color: #c2410c; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Factory BOM & Material Requirement Calculator")
st.write("Select a product, enter production quantity, enter available stock if known, and prepare the purchase order list.")

tabs = st.tabs(["Calculator", "Add / Edit Products", "Product Catalogue"])

with tabs[0]:
    st.header("Step 1: Select Production Details")

    category_filter = st.selectbox(
        "Filter by Product Category",
        ["All Categories"] + sorted(set(p.get("category", "Uncategorised") for p in st.session_state.products.values()))
    )

    product_options = list(st.session_state.products.keys())
    if category_filter != "All Categories":
        product_options = [p for p in product_options if st.session_state.products[p].get("category") == category_filter]

    col1, col2, col3 = st.columns(3)
    with col1:
        product_name = st.selectbox("Product / Model", product_options)
        product = st.session_state.products[product_name]
        st.caption(product.get("description", ""))
        st.caption(f"Status: {product.get('bom_status', 'BOM PENDING')}")
    with col2:
        production_qty = st.number_input("How many finished pieces to make?", min_value=0, value=1000, step=1)
    with col3:
        wastage_percent = st.number_input("Material wastage %", min_value=0.0, value=0.0, step=0.5)

    if len(product["components"]) == 0:
        st.markdown(
            '<div class="pending-box"><b>BOM Pending:</b> This product is listed in the public company catalogue, '
            'but its internal material list has not been added yet. Add components in the Add / Edit Products tab, '
            'or upload the BOM sheet for this product.</div>',
            unsafe_allow_html=True
        )
        st.stop()

    df = calculate_requirements(product_name, production_qty, wastage_percent)

    enough_count = int((df["Status"] == "Enough Stock").sum())
    order_count = int((df["Status"] == "Order Required").sum())
    pieces_to_order = df[df["Unit"] == "pcs"]["Quantity To Order"].sum()
    mm_to_order = df[df["Unit"] == "mm"]["Quantity To Order"].sum()

    st.header("Step 2: Stock Summary")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Enough Stock Lines", enough_count)
    m2.metric("Lines Needing Order", order_count)
    m3.metric("Pieces To Order", f"{pieces_to_order:,.0f} pcs")
    m4.metric("MM Material To Order", f"{mm_to_order / 1000:,.2f} m")

    st.markdown(
        '<div class="warning-box"><b>Important:</b> Enter stock in the same unit shown in the Unit column. '
        'For wire in mm, enter stock in millimetres. Example: 500 metres = 500000 mm. '
        'If stock is left blank, the app treats it as 0 and still calculates the full required material.</div>',
        unsafe_allow_html=True
    )

    st.header("Step 3: Enter Current Stock")
    for idx, row in df.iterrows():
        with st.container(border=True):
            left, mid, right = st.columns([2.2, 1.4, 1.2])
            with left:
                st.subheader(row["Component Name"])
                st.write(f"**Specification:** {row['Specification']}")
                st.write(f"**Needed Per Finished Piece:** {format_qty(row['Required Per Unit'], row['Unit'])}")
            with mid:
                st.write("**Total Needed**")
                st.write(format_qty(row["Total Needed"], row["Unit"]))
                st.write("**Current Status**")
                if row["Status"] == "Enough Stock":
                    st.markdown('<span class="success-text">Enough Stock</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="danger-text">Order Required</span>', unsafe_allow_html=True)
            with right:
                stock_value = st.number_input(
                    f"Stock In Hand ({row['Unit']})",
                    min_value=0.0,
                    value=float(st.session_state.stock.get(row["Stock Key"], 0) or 0),
                    step=1.0,
                    key=f"stock_{row['Stock Key']}"
                )
                st.session_state.stock[row["Stock Key"]] = stock_value

    df = calculate_requirements(product_name, production_qty, wastage_percent)

    st.header("Final Order List")
    st.dataframe(apply_table_formatting(df), use_container_width=True, hide_index=True)

    csv = make_csv(df, product_name, production_qty)
    st.download_button(
        label="⬇️ Download Order Sheet CSV",
        data=csv,
        file_name=f"{product_name.replace(' ', '_').replace('/', '-')}_order_sheet.csv",
        mime="text/csv"
    )

with tabs[1]:
    st.header("Add / Edit Products")
    st.write("Use this section to add full BOMs for public catalogue items or new products made by the company.")

    with st.expander("Add New Product", expanded=True):
        new_name = st.text_input("New Product / Model Name")
        new_category = st.text_input("Category", value="Uncategorised")
        new_description = st.text_input("Description")
        if st.button("Create Product"):
            if not new_name.strip():
                st.error("Enter a product name.")
            elif new_name.strip() in st.session_state.products:
                st.error("This product already exists.")
            else:
                st.session_state.products[new_name.strip()] = {
                    "category": new_category.strip() or "Uncategorised",
                    "description": new_description.strip(),
                    "bom_status": "BOM PENDING",
                    "components": []
                }
                st.success(f"Product created: {new_name.strip()}")

    st.divider()

    selected_product_for_edit = st.selectbox("Select product to edit", list(st.session_state.products.keys()), key="edit_product")
    product = st.session_state.products[selected_product_for_edit]

    product["category"] = st.text_input("Product Category", value=product.get("category", "Uncategorised"))
    product["description"] = st.text_input("Product Description", value=product.get("description", ""))
    product["bom_status"] = "BOM READY" if len(product["components"]) > 0 else "BOM PENDING"

    st.subheader("Add Component to Product")
    c1, c2, c3, c4 = st.columns([1.6, 2, 0.8, 1])
    with c1:
        comp_name = st.text_input("Component Name")
    with c2:
        comp_spec = st.text_input("Specification")
    with c3:
        comp_unit = st.selectbox("Unit", ALLOWED_UNITS)
    with c4:
        comp_required = st.number_input("Required Per Unit", min_value=0.0, value=1.0, step=1.0)

    if st.button("Add Component"):
        if not comp_name.strip():
            st.error("Enter a component name.")
        else:
            product["components"].append({
                "Component Name": comp_name.strip(),
                "Specification": comp_spec.strip(),
                "Unit": comp_unit,
                "Required Per Unit": float(comp_required)
            })
            product["bom_status"] = "BOM READY"
            st.success("Component added.")

    st.subheader("Current Components")
    if product["components"]:
        st.dataframe(pd.DataFrame(product["components"]), use_container_width=True, hide_index=True)
        delete_index = st.number_input("Component row number to delete. First row is 1.", min_value=1, max_value=len(product["components"]), value=1, step=1)
        if st.button("Delete Selected Component"):
            removed = product["components"].pop(delete_index - 1)
            product["bom_status"] = "BOM READY" if product["components"] else "BOM PENDING"
            st.warning(f"Deleted: {removed['Component Name']}")
    else:
        st.info("No components added yet.")

with tabs[2]:
    st.header("Product Catalogue")
    st.write("Public product families have been preloaded as placeholders. Only SHINE NEW and SHINE OLD have full BOM data from the Excel sheet.")

    rows = []
    for pname, pdata in st.session_state.products.items():
        rows.append({
            "Product / Model": pname,
            "Category": pdata.get("category", "Uncategorised"),
            "BOM Status": "BOM READY" if len(pdata.get("components", [])) else "BOM PENDING",
            "Component Lines": len(pdata.get("components", [])),
            "Description": pdata.get("description", "")
        })

    catalogue_df = pd.DataFrame(rows).sort_values(["Category", "Product / Model"])
    st.dataframe(catalogue_df, use_container_width=True, hide_index=True)

    st.subheader("Full BOM View")
    for pname, pdata in st.session_state.products.items():
        with st.expander(pname):
            st.write(f"**Category:** {pdata.get('category', 'Uncategorised')}")
            st.write(f"**Description:** {pdata.get('description', '')}")
            if pdata["components"]:
                st.dataframe(pd.DataFrame(pdata["components"]), use_container_width=True, hide_index=True)
            else:
                st.info("BOM not added yet.")
