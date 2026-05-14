# ECL Material Calculator

A simple internal factory material calculator for ECL India / ECL Magtronics.

## What it does

Select a product (SHINE NEW or SHINE OLD), enter how many pieces you want to make, optionally enter current stock, and the app calculates exactly what needs to be ordered.

## Products supported

- **SHINE NEW** — New Shine stator wire harness
- **SHINE OLD** — Old Shine stator wire harness

## How to run locally

```bash
pip install streamlit pandas
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub repo.
4. Set the main file path to `app.py`.
5. Click Deploy.

## Unit reminder for users

- For **parts/components**: enter quantities in **pieces (pcs)**.
- For **wire**: enter lengths in **millimetres (mm)**. Example: 500 metres = 500,000 mm.

## File structure

```
ecl_calculator/
├── app.py
├── requirements.txt
├── runtime.txt
├── README.md
└── .streamlit/
    └── config.toml
```

## Adding more products

Open `app.py` and add a new entry to the `PRODUCTS` dictionary following the same format as SHINE NEW or SHINE OLD. No other changes needed.
