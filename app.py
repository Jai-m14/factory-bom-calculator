from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ECL Material Planner",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Default BOM data
# -----------------------------------------------------------------------------

Product = Dict[str, object]

DEFAULT_PRODUCTS: Dict[str, Product] = {
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

CATALOGUE_PLACEHOLDERS = [
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

# -----------------------------------------------------------------------------
# State and helpers
# -----------------------------------------------------------------------------


def initialise_state() -> None:
    if "products" not in st.session_state:
        products = {name: data.copy() for name, data in DEFAULT_PRODUCTS.items()}
        for name, category in CATALOGUE_PLACEHOLDERS:
            products.setdefault(
                name,
                {
                    "category": category,
                    "description": "Catalogue placeholder. Add internal BOM before calculation.",
                    "components": [],
                },
            )
        st.session_state.products = products

    if "stock" not in st.session_state:
        st.session_state.stock = {}


initialise_state()


def component_key(row: pd.Series | dict) -> str:
    return f"{row['Component Name']}|{row['Specification']}|{row['Unit']}"


def format_quantity(value: float, unit: str) -> str:
    value = float(value or 0)
    if unit == "pcs":
        return f"{value:,.0f} pcs"
    if unit == "mm":
        return f"{value:,.0f} mm ({value / 1000:,.2f} m)"
    if unit in {"m", "kg", "g", "litre", "ml"}:
        return f"{value:,.2f} {unit}"
    return f"{value:,.2f} {unit}"


def product_dataframe(product_name: str) -> pd.DataFrame:
    product = st.session_state.products[product_name]
    df = pd.DataFrame(product["components"])
    if df.empty:
        return pd.DataFrame(columns=["Component Name", "Specification", "Unit", "Required Per Unit", "Stock In Hand"])

    df["Required Per Unit"] = pd.to_numeric(df["Required Per Unit"], errors="coerce").fillna(0.0)
    df["Stock In Hand"] = [float(st.session_state.stock.get(component_key(row), 0) or 0) for _, row in df.iterrows()]
    return df


def save_stock(df: pd.DataFrame) -> None:
    for _, row in df.iterrows():
        st.session_state.stock[component_key(row)] = float(row.get("Stock In Hand", 0) or 0)


def calculate_requirements(df: pd.DataFrame, quantity: int, wastage_percent: float) -> pd.DataFrame:
    result = df.copy()
    if result.empty:
        return result

    result["Required Per Unit"] = pd.to_numeric(result["Required Per Unit"], errors="coerce").fillna(0.0)
    result["Stock In Hand"] = pd.to_numeric(result["Stock In Hand"], errors="coerce").fillna(0.0)
    result["Total Needed"] = result["Required Per Unit"] * quantity

    wastage_units = result["Unit"].isin(["mm", "m", "kg", "g", "litre", "ml"])
    result.loc[wastage_units, "Total Needed"] *= 1 + (wastage_percent / 100)

    result["Quantity To Order"] = (result["Total Needed"] - result["Stock In Hand"]).clip(lower=0)
    result["Balance After Production"] = result["Stock In Hand"] - result["Total Needed"]
    result["Status"] = result["Quantity To Order"].apply(lambda x: "Enough Stock" if x <= 0 else "Order Required")
    return result


def display_table(result: pd.DataFrame) -> pd.DataFrame:
    table = result.copy()
    for col in ["Required Per Unit", "Total Needed", "Stock In Hand", "Quantity To Order", "Balance After Production"]:
        table[col] = [format_quantity(value, unit) for value, unit in zip(table[col], table["Unit"])]
    return table[
        [
            "Component Name",
            "Specification",
            "Unit",
            "Required Per Unit",
            "Total Needed",
            "Stock In Hand",
            "Quantity To Order",
            "Balance After Production",
            "Status",
        ]
    ]


def export_csv(result: pd.DataFrame, product_name: str, quantity: int) -> bytes:
    export = result.copy()
    export.insert(0, "Product / Model", product_name)
    export.insert(1, "Production Quantity", quantity)
    export.insert(2, "Generated At", datetime.now().strftime("%Y-%m-%d %H:%M"))
    return export.to_csv(index=False).encode("utf-8")


def product_catalogue_df() -> pd.DataFrame:
    rows = []
    for name, data in st.session_state.products.items():
        component_count = len(data.get("components", []))
        rows.append(
            {
                "Product / Model": name,
                "Category": data.get("category", "Uncategorised"),
                "BOM Status": "Ready" if component_count else "Pending",
                "Material Lines": component_count,
                "Description": data.get("description", ""),
            }
        )
    return pd.DataFrame(rows).sort_values(["Category", "Product / Model"])


# -----------------------------------------------------------------------------
# Minimal styling only. Do not override Streamlit widget text colours globally.
# -----------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            max-width: 1220px;
        }
        .ecl-header {
            background: #ffffff;
            border: 1px solid #d7dee8;
            border-left: 7px solid #1f4e8c;
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 18px;
        }
        .ecl-kicker {
            color: #1f4e8c;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-size: 0.82rem;
            margin-bottom: 6px;
        }
        .ecl-title {
            color: #172033;
            font-size: 2.15rem;
            line-height: 1.12;
            font-weight: 800;
            margin: 0;
        }
        .ecl-subtitle {
            color: #5b6675;
            font-size: 1rem;
            margin-top: 8px;
            max-width: 840px;
        }
        .ecl-panel {
            background: #ffffff;
            border: 1px solid #d7dee8;
            border-radius: 16px;
            padding: 20px 22px;
            margin-bottom: 18px;
        }
        .ecl-help {
            color: #5b6675;
            font-size: 0.95rem;
            margin-bottom: 14px;
        }
        .unit-note {
            background: #fff8e8;
            border: 1px solid #efc96b;
            border-radius: 12px;
            padding: 12px 14px;
            color: #664300;
            margin-bottom: 14px;
        }
        .status-ready {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            background: #e9f7ef;
            color: #166534;
            border: 1px solid #b7e2c4;
            font-weight: 800;
            font-size: 0.78rem;
        }
        .status-pending {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            background: #fff3e2;
            color: #9a3412;
            border: 1px solid #ffc489;
            font-weight: 800;
            font-size: 0.78rem;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #d7dee8;
            border-radius: 14px;
            padding: 14px 16px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------

st.markdown(
    """
    <div class="ecl-header">
        <div class="ecl-kicker">ECL India • Internal Factory Tool</div>
        <div class="ecl-title">Material Requirement Planner</div>
        <div class="ecl-subtitle">
            Calculate production material requirements, compare stock in hand, and prepare purchase order sheets.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

calculator_tab, manager_tab, catalogue_tab = st.tabs(["Production Calculator", "BOM Manager", "Product Catalogue"])

# -----------------------------------------------------------------------------
# Production Calculator
# -----------------------------------------------------------------------------

with calculator_tab:
    st.markdown('<div class="ecl-panel">', unsafe_allow_html=True)
    st.subheader("Production setup")
    st.markdown('<div class="ecl-help">Select product, enter quantity, and optionally add material wastage.</div>', unsafe_allow_html=True)

    product_names = list(st.session_state.products.keys())
    c1, c2, c3, c4 = st.columns([1.7, 1, 1, 0.8])

    with c1:
        product_name = st.selectbox("Product / Model", product_names)
    with c2:
        quantity = st.number_input("Production Quantity", min_value=0, value=1000, step=1)
    with c3:
        wastage = st.number_input("Wastage %", min_value=0.0, value=0.0, step=0.5)
    with c4:
        selected_product = st.session_state.products[product_name]
        st.write("BOM Status")
        badge_class = "status-ready" if selected_product["components"] else "status-pending"
        badge_text = "READY" if selected_product["components"] else "PENDING"
        st.markdown(f'<span class="{badge_class}">{badge_text}</span>', unsafe_allow_html=True)

    st.caption(f"{selected_product.get('category', '')} • {selected_product.get('description', '')}")
    st.markdown('</div>', unsafe_allow_html=True)

    if not selected_product["components"]:
        st.info("This catalogue item is saved as a placeholder. Add its internal BOM in BOM Manager before calculating material.")
    else:
        df = product_dataframe(product_name)

        st.markdown('<div class="ecl-panel">', unsafe_allow_html=True)
        st.subheader("Stock entry")
        st.markdown('<div class="ecl-help">Only edit the Stock In Hand column. Leave stock as 0 when current stock is unknown.</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="unit-note"><b>Unit rule:</b> Enter stock in the unit shown. For wire in mm, enter millimetres. Example: 500 metres = 500000 mm.</div>',
            unsafe_allow_html=True,
        )

        edited_df = st.data_editor(
            df,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=["Component Name", "Specification", "Unit", "Required Per Unit"],
            column_config={
                "Component Name": st.column_config.TextColumn("Material Name", width="medium"),
                "Specification": st.column_config.TextColumn("Specification", width="large"),
                "Unit": st.column_config.TextColumn("Unit", width="small"),
                "Required Per Unit": st.column_config.NumberColumn("Required / Unit", format="%.2f", width="small"),
                "Stock In Hand": st.column_config.NumberColumn("Stock In Hand", min_value=0.0, step=1.0, format="%.2f", width="small"),
            },
            key=f"stock_editor_{product_name}",
        )
        save_stock(edited_df)
        st.markdown('</div>', unsafe_allow_html=True)

        result = calculate_requirements(edited_df, quantity, wastage)

        enough = int((result["Status"] == "Enough Stock").sum())
        need_order = int((result["Status"] == "Order Required").sum())
        pieces_to_order = result[result["Unit"].eq("pcs")]["Quantity To Order"].sum()
        wire_to_order_mm = result[result["Unit"].eq("mm")]["Quantity To Order"].sum()

        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("BOM Lines", len(result))
        s2.metric("Enough Stock", enough)
        s3.metric("Need Order", need_order)
        s4.metric("Pieces To Order", f"{pieces_to_order:,.0f}")
        s5.metric("Wire To Order", f"{wire_to_order_mm / 1000:,.2f} m")

        st.markdown('<div class="ecl-panel">', unsafe_allow_html=True)
        st.subheader("Final order sheet")
        st.markdown('<div class="ecl-help">Download this table for purchase planning or stores verification.</div>', unsafe_allow_html=True)

        final_table = display_table(result)

        def colour_status(row):
            styles = [""] * len(row)
            status_idx = row.index.get_loc("Status")
            order_idx = row.index.get_loc("Quantity To Order")
            if row["Status"] == "Order Required":
                styles[status_idx] = "background-color: #fff3e2; color: #9a3412; font-weight: 700;"
                styles[order_idx] = "color: #9a3412; font-weight: 700;"
            else:
                styles[status_idx] = "background-color: #e9f7ef; color: #166534; font-weight: 700;"
            return styles

        st.dataframe(final_table.style.apply(colour_status, axis=1), use_container_width=True, hide_index=True)

        st.download_button(
            "Download Order Sheet CSV",
            data=export_csv(result, product_name, quantity),
            file_name=f"{product_name.replace(' ', '_').replace('/', '-')}_order_sheet.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BOM Manager
# -----------------------------------------------------------------------------

with manager_tab:
    st.markdown('<div class="ecl-panel">', unsafe_allow_html=True)
    st.subheader("BOM Manager")
    st.markdown('<div class="ecl-help">Use this section to add or edit BOMs for future ECL products.</div>', unsafe_allow_html=True)

    selected = st.selectbox("Product to edit", list(st.session_state.products.keys()), key="manager_product")
    product = st.session_state.products[selected]

    m1, m2 = st.columns([1, 2])
    with m1:
        product["category"] = st.text_input("Category", value=product.get("category", "Uncategorised"))
    with m2:
        product["description"] = st.text_input("Description", value=product.get("description", ""))

    st.markdown("#### Current BOM")
    if product["components"]:
        bom_df = pd.DataFrame(product["components"])
        edited_bom = st.data_editor(
            bom_df,
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Unit": st.column_config.SelectboxColumn("Unit", options=ALLOWED_UNITS),
                "Required Per Unit": st.column_config.NumberColumn("Required Per Unit", min_value=0.0, step=1.0),
            },
            key=f"bom_editor_{selected}",
        )
        product["components"] = edited_bom.to_dict("records")
    else:
        st.info("No BOM added for this product yet.")

    st.markdown("#### Add component")
    a1, a2, a3, a4 = st.columns([1.2, 2, 0.8, 1])
    with a1:
        component_name = st.text_input("Component Name")
    with a2:
        specification = st.text_input("Specification")
    with a3:
        unit = st.selectbox("Unit", ALLOWED_UNITS)
    with a4:
        required_per_unit = st.number_input("Required / Unit", min_value=0.0, value=1.0, step=1.0)

    if st.button("Add Component", use_container_width=True):
        if not component_name.strip():
            st.error("Component name is required.")
        else:
            product["components"].append(
                {
                    "Component Name": component_name.strip(),
                    "Specification": specification.strip(),
                    "Unit": unit,
                    "Required Per Unit": float(required_per_unit),
                }
            )
            st.success("Component added. It will appear after the next refresh/rerun.")

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Product Catalogue
# -----------------------------------------------------------------------------

with catalogue_tab:
    st.markdown('<div class="ecl-panel">', unsafe_allow_html=True)
    st.subheader("ECL Product Catalogue")
    st.markdown('<div class="ecl-help">Products marked Ready can be calculated. Pending products need their internal BOM added first.</div>', unsafe_allow_html=True)

    catalogue = product_catalogue_df()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Products", len(catalogue))
    c2.metric("BOM Ready", int((catalogue["BOM Status"] == "Ready").sum()))
    c3.metric("BOM Pending", int((catalogue["BOM Status"] == "Pending").sum()))

    st.dataframe(catalogue, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.caption("ECL India internal material planning tool")
