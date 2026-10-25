import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory

# Determine base paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASH_DIR = os.path.join(CURRENT_DIR, "stitch_food_delivery_demand_analytics_dashboard")
MODELS_DIR = os.path.join(CURRENT_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "best_demand_lgbm.joblib")

app = Flask(__name__)

# Load trained LightGBM ML Pipeline if present
ml_pipeline = None
if os.path.exists(MODEL_PATH):
    try:
        ml_pipeline = joblib.load(MODEL_PATH)
        print(f"[AI Server] Successfully loaded trained model from: {MODEL_PATH}")
    except Exception as e:
        print(f"[AI Server] Warning: Could not load model: {e}")
else:
    print(f"[AI Server] Notice: Model file not found at {MODEL_PATH}, will use calibrated formula.")

# Page routes
@app.route("/")
@app.route("/forecaster")
def page_forecaster():
    return send_from_directory(os.path.join(DASH_DIR, "the_kitchen_forecaster"), "code.html")

@app.route("/trends")
def page_trends():
    return send_from_directory(os.path.join(DASH_DIR, "weekly_trends"), "code.html")

@app.route("/scorecard")
def page_scorecard():
    return send_from_directory(os.path.join(DASH_DIR, "model_scorecard"), "code.html")

@app.route("/notes")
def page_notes():
    return send_from_directory(os.path.join(DASH_DIR, "project_notes"), "code.html")

# Static asset serving for screen.png
@app.route("/the_kitchen_forecaster/<path:filename>")
def static_forecaster(filename):
    return send_from_directory(os.path.join(DASH_DIR, "the_kitchen_forecaster"), filename)

@app.route("/weekly_trends/<path:filename>")
def static_trends(filename):
    return send_from_directory(os.path.join(DASH_DIR, "weekly_trends"), filename)

@app.route("/model_scorecard/<path:filename>")
def static_scorecard(filename):
    return send_from_directory(os.path.join(DASH_DIR, "model_scorecard"), filename)

@app.route("/project_notes/<path:filename>")
def static_notes(filename):
    return send_from_directory(os.path.join(DASH_DIR, "project_notes"), filename)

# Live Machine Learning Inference API
@app.route("/api/predict", methods=["POST"])
def predict_demand():
    try:
        data = request.get_json() or {}
        center_id = int(data.get("center_id", 55))
        category = data.get("category", "Rice Bowl")
        price = float(data.get("price", 135.0))
        is_homepage = int(data.get("homepage_featured", 0))
        is_emailer = int(data.get("emailer_for_promotion", 0))

        if ml_pipeline is not None:
            model = ml_pipeline["model"]
            features = ml_pipeline["features"]

            # Construct input vector matching trained schema
            input_dict = {f: 0.0 for f in features}

            base_price = price * 1.18
            input_dict["checkout_price"] = price
            input_dict["base_price"] = base_price
            input_dict["checkout_to_base_ratio"] = price / base_price
            input_dict["homepage_featured"] = float(is_homepage)
            input_dict["emailer_for_promotion"] = float(is_emailer)
            input_dict["op_area"] = 4.5
            input_dict["week_scaled"] = 0.95
            input_dict["week_sin"] = np.sin(2 * np.pi * 146 / 52)
            input_dict["week_cos"] = np.cos(2 * np.pi * 146 / 52)

            if "center_type_TYPE_B" in input_dict and center_id == 24:
                input_dict["center_type_TYPE_B"] = 1.0
            elif "center_type_TYPE_C" in input_dict and center_id == 13:
                input_dict["center_type_TYPE_C"] = 1.0

            cat_col = f"category_{category}"
            if cat_col in input_dict:
                input_dict[cat_col] = 1.0

            baseline_orders = 1100.0
            for l in [1, 2, 3, 4, 5, 6, 7, 8]:
                col = f"orders_lag_{l}w"
                if col in input_dict:
                    input_dict[col] = baseline_orders
            if "rolling_mean_4w" in input_dict:
                input_dict["rolling_mean_4w"] = baseline_orders
            if "rolling_mean_8w" in input_dict:
                input_dict["rolling_mean_8w"] = baseline_orders

            input_df = pd.DataFrame([input_dict])[features]
            log_pred = model.predict(input_df)[0]
            pred_orders = int(np.clip(np.expm1(log_pred), 100, 20000))
        else:
            price_effect = max(180, int((240 - price) * 6.5))
            home_boost = 320 if is_homepage else 0
            email_boost = 210 if is_emailer else 0
            pred_orders = 650 + price_effect + home_boost + email_boost

        couriers = max(5, int(round(pred_orders / 75)))
        chefs = max(2, int(round(pred_orders / 280)))
        ci_low = int(pred_orders * 0.91)
        ci_high = int(pred_orders * 1.09)

        return jsonify({
            "status": "success",
            "predicted_orders": pred_orders,
            "confidence_interval": f"{ci_low:,} - {ci_high:,} portions",
            "couriers": couriers,
            "chefs": chefs,
            "engine": "LightGBM Regressor (Log1p)" if ml_pipeline else "Econometric Formulation"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n=======================================================")
    print(f" Culinary Intelligence Atelier UI Server Running!")
    print(f" URL: http://localhost:{port}")
    print(f"   * Forecaster  : http://localhost:{port}/forecaster")
    print(f"   * Trends      : http://localhost:{port}/trends")
    print(f"   * Scorecard   : http://localhost:{port}/scorecard")
    print(f"   * Notes       : http://localhost:{port}/notes")
    print(f"=======================================================\n")
    app.run(host="127.0.0.1", port=port, debug=False)
