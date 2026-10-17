# Flask backend that serves the SuperKart sales forecasting model

import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Predictor")

# Load the trained model pipeline (preprocessing + tuned Random Forest)
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in the order used during training
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Home route - a simple health check
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Prediction API!"


# Online inference: predict sales for a single product-store record sent as JSON
@superkart_api.post("/v1/predict")
def predict_sales():
    # Get the JSON data from the request body
    product_data = request.get_json(silent=True)
    if not product_data:
        return jsonify({"error": "Request body must be a JSON object with the product and store details."}), 400

    # Check that every required feature is present
    missing = [f for f in FEATURES if f not in product_data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Convert the input into a single-row DataFrame with the expected columns
    input_df = pd.DataFrame([{f: product_data[f] for f in FEATURES}])

    # Make the prediction
    prediction = model.predict(input_df)[0]

    # Return the prediction rounded to 2 decimals
    return jsonify({"Predicted Sales (in dollars)": round(float(prediction), 2)})


# Batch inference: predict sales for every row of an uploaded CSV file
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    # Get the uploaded CSV file from the request
    if "file" not in request.files:
        return jsonify({"error": "Please upload a CSV file using the 'file' key."}), 400
    input_data = pd.read_csv(request.files["file"])

    # Check that every required feature is present
    missing = [f for f in FEATURES if f not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing columns in CSV: {missing}"}), 400

    # Make predictions for all rows
    predictions = model.predict(input_data[FEATURES])

    # Return a dictionary of {row index: predicted sales}
    output = {str(idx): round(float(pred), 2) for idx, pred in zip(input_data.index, predictions)}
    return jsonify(output)


# Run the app locally (inside Docker, gunicorn is used instead)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
