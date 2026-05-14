
# Factory BOM & Material Requirement Calculator

This is a Python Streamlit app for a small auto-parts/electrical-parts factory.

## What it does

- Select a product/model
- Enter production quantity
- Enter current stock if known
- If stock is blank, it treats stock as 0
- Calculates total material required
- Calculates quantity to order
- Shows balance after production
- Exports order sheet as CSV
- Allows adding new products and components later

## Preloaded data

Full BOM data:
- SHINE NEW
- SHINE OLD

Public ECL catalogue placeholders:
- Horns DC
- Horns AC
- Stators
- Source Coils
- Light Coils
- Ignition Coils
- Igniters
- CDI Units
- Regulator Rectifiers
- Starter Relays
- Flashers
- Buzzers

The public catalogue entries are placeholders only. Add BOM components when internal material sheets are available.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Best deployment route:
- GitHub + Streamlit Community Cloud

Netlify is not recommended for this Python Streamlit app.
