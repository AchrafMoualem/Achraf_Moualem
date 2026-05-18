# app.py — Store Sales Prediction
# Run: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler

# ── Load model components ─────────────────────────────────────────────────────
with open("rf_model.pkl", "rb") as f:
    components = pickle.load(f)

num_imputer = components["num_imputer"]
cat_imputer = components["cat_imputer"]
encoder     = components["encoder"]
model       = components["model"]
scaler      = StandardScaler()

# ── Column definitions ────────────────────────────────────────────────────────
categorical_columns = ["family", "store_type", "city", "state"]
numerical_columns   = ["store_nbr", "onpromotion", "cluster", "transactions",
                       "oil_price", "month", "day", "dayofweek"]

# ── Family groupings (same as training) ───────────────────────────────────────
food_families       = ["BEVERAGES", "BREAD/BAKERY", "DAIRY", "DELI", "EGGS",
                       "FROZEN FOODS", "MEATS", "POULTRY", "PREPARED FOODS", "SEAFOOD"]
home_families       = ["HOME AND KITCHEN I", "HOME AND KITCHEN II", "HOME APPLIANCES"]
clothing_families   = ["CLOTHING", "LADIESWEAR", "BABY CARE"]
grocery_families    = ["GROCERY I", "GROCERY II", "PRODUCE"]
stationery_families = ["STATIONERY", "BOOKS", "MAGAZINES"]
cleaning_families   = ["HOME CARE", "PERSONAL CARE", "CLEANING"]
hardware_families   = ["HARDWARE", "TOOLS", "LAWN AND GARDEN", "GARDEN"]

all_families = sorted(set(
    food_families + home_families + clothing_families + grocery_families +
    stationery_families + cleaning_families + hardware_families +
    ["AUTOMOTIVE", "BEAUTY", "CELEBRATION", "ELECTRONICS",
     "LIQUOR,WINE,BEER", "LINGERIE", "MUSIC", "PET SUPPLIES",
     "PLAYERS AND ELECTRONICS", "SCHOOL AND OFFICE SUPPLIES"]
))

# ── Page setup ────────────────────────────────────────────────────────────────
st.title("🛒 Store Sales Predictor")
st.caption("Enter store details to predict daily sales.")

# ── Sidebar descriptions ──────────────────────────────────────────────────────
st.sidebar.header("Input Field Descriptions")
st.sidebar.markdown("**Store Number**: ID of the store (0–54).")
st.sidebar.markdown("**Product Family**: Category of products being sold.")
st.sidebar.markdown("**On Promotion**: Number of items currently on promotion.")
st.sidebar.markdown("**Store Type**: Type classification of the store (A–E).")
st.sidebar.markdown("**City**: City where the store is located.")
st.sidebar.markdown("**State**: State where the store is located.")
st.sidebar.markdown("**Cluster**: Store cluster group (0–16).")
st.sidebar.markdown("**Transactions**: Number of transactions on that day.")
st.sidebar.markdown("**Crude Oil Price**: Daily oil price in USD.")
st.sidebar.markdown("**Month / Day / Day of Week**: Date information.")

# ── Input fields ──────────────────────────────────────────────────────────────
input_data = {}
col1, col2, col3 = st.columns(3)

with col1:
    input_data["store_nbr"]    = st.slider("Store Number", 0, 54, 1)
    input_data["family"]       = st.selectbox("Product Family", all_families)
    input_data["onpromotion"]  = st.number_input("Items on Promotion", min_value=0, value=0)
    input_data["state"]        = st.selectbox("State", [
        "Pichincha", "Cotopaxi", "Chimborazo", "Imbabura",
        "Santo Domingo de los Tsachilas", "Bolivar", "Pastaza",
        "Tungurahua", "Guayas", "Santa Elena", "Los Rios",
        "Azuay", "Loja", "El Oro", "Esmeraldas", "Manabi",
    ])
    input_data["transactions"] = st.number_input("Transactions", min_value=0, value=500)

with col2:
    input_data["store_type"] = st.selectbox("Store Type", ["A", "B", "C", "D", "E"])
    input_data["cluster"]    = st.slider("Cluster", 0, 16, 1)
    input_data["city"]       = st.selectbox("City", [
        "Quito", "Guayaquil", "Cuenca", "Ambato", "Manta",
        "Riobamba", "Ibarra", "Loja", "Esmeraldas", "Machala",
        "Latacunga", "Libertad", "Puyo", "Salinas", "Daule", "Cayambe",
    ])
    input_data["oil_price"]  = st.number_input("Crude Oil Price (USD)", min_value=0.0, value=50.0)

with col3:
    input_data["month"]     = st.slider("Month", 1, 12, 1)
    input_data["day"]       = st.slider("Day", 1, 31, 1)
    input_data["dayofweek"] = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, 0)

# ── Predict button ────────────────────────────────────────────────────────────
if st.button("Predict Sales"):
    input_df = pd.DataFrame([input_data])

    # Group families (same logic as training)
    input_df["family"] = np.where(input_df["family"].isin(food_families),       "FOODS",      input_df["family"])
    input_df["family"] = np.where(input_df["family"].isin(home_families),       "HOME",       input_df["family"])
    input_df["family"] = np.where(input_df["family"].isin(clothing_families),   "CLOTHING",   input_df["family"])
    input_df["family"] = np.where(input_df["family"].isin(grocery_families),    "GROCERY",    input_df["family"])
    input_df["family"] = np.where(input_df["family"].isin(stationery_families), "STATIONERY", input_df["family"])
    input_df["family"] = np.where(input_df["family"].isin(cleaning_families),   "CLEANING",   input_df["family"])
    input_df["family"] = np.where(input_df["family"].isin(hardware_families),   "HARDWARE",   input_df["family"])

    # Split into categorical and numerical
    input_df_cat = input_df[categorical_columns].copy()
    input_df_num = input_df[numerical_columns].copy()

    # Impute
    input_df_cat_imputed = cat_imputer.transform(input_df_cat)
    input_df_num_imputed = num_imputer.transform(input_df_num)

    # Encode categorical
    input_df_cat_encoded = pd.DataFrame(
        encoder.transform(input_df_cat_imputed).toarray(),
        columns=encoder.get_feature_names_out(categorical_columns),
    )

    # Scale numerical
    input_df_num_scaled = scaler.fit_transform(input_df_num_imputed)
    input_df_num_sc     = pd.DataFrame(input_df_num_scaled, columns=numerical_columns)

    # Combine and predict
    input_df_processed = pd.concat([input_df_cat_encoded, input_df_num_sc], axis=1)
    predictions        = model.predict(input_df_processed)

    st.success(f"💰 Predicted Sales: **{predictions[0]:,.2f}**")
