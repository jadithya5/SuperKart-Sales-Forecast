# Streamlit frontend for the SuperKart sales forecasting API

import os

import pandas as pd
import requests
import streamlit as st

# URL of the Flask backend.
# Inside the Docker network the backend container is reachable by its container name.
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Sales Forecast")
st.write("Predict the total sales revenue of a product in a SuperKart store.")

# ---------------- Online prediction ----------------
st.subheader("Online Prediction")

col1, col2 = st.columns(2)
with col1:
    product_weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
    product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    product_allocated_area = st.number_input(
        "Product Allocated Area (ratio of display area)", min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f"
    )
    product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08, step=0.01)
    product_id_char = st.selectbox("Product Id Prefix (FD = Food, DR = Drinks, NC = Non-Consumable)", ["FD", "DR", "NC"])
with col2:
    store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    store_location_city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
    store_type = st.selectbox(
        "Store Type", ["Departmental Store", "Supermarket Type1", "Supermarket Type2", "Food Mart"]
    )
    store_age_years = st.number_input("Store Age (years)", min_value=0, max_value=100, value=16, step=1)
    product_type_category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

# Collect the user input in the format expected by the API
product_data = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": product_sugar_content,
    "Product_Allocated_Area": product_allocated_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": store_location_city_type,
    "Store_Type": store_type,
    "Product_Id_char": product_id_char,
    "Store_Age_Years": int(store_age_years),
    "Product_Type_Category": product_type_category,
}

if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data, timeout=30)
        if response.status_code == 200:
            prediction = response.json()["Predicted Sales (in dollars)"]
            st.success(f"Predicted Product Store Sales Total: ${prediction:,.2f}")
        else:
            st.error(f"Error from the API ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")

# ---------------- Batch prediction ----------------
st.subheader("Batch Prediction")
st.write("Upload a CSV file with the same 10 feature columns to get predictions for every row.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
if uploaded_file is not None and st.button("Predict Batch"):
    try:
        response = requests.post(
            f"{BACKEND_URL}/v1/predictbatch",
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
            timeout=60,
        )
        if response.status_code == 200:
            predictions = response.json()
            batch_df = pd.read_csv(uploaded_file)
            batch_df["Predicted_Sales"] = [predictions[str(i)] for i in batch_df.index]
            st.success("Batch predictions completed!")
            st.dataframe(batch_df)
            st.download_button(
                "Download predictions as CSV",
                batch_df.to_csv(index=False).encode("utf-8"),
                file_name="superkart_predictions.csv",
                mime="text/csv",
            )
        else:
            st.error(f"Error from the API ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")
