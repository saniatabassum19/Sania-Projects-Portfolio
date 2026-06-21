import os
import re
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor

try:
    from catboost import CatBoostRegressor
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

DATA_PATH = os.path.join(os.path.dirname(__file__), "Airbnb Data", "Airbnb_Data.csv")

st.set_page_config(
    page_title="Airbnb Price Predictor",
    page_icon="🏡",
    layout="wide",
)


def parse_response_rate(value):
    if pd.isna(value):
        return 0.0
    value = str(value).strip()
    value = value.replace('%', '').replace(',', '').strip()
    try:
        return float(value)
    except ValueError:
        return 0.0


def count_amenities(value):
    if pd.isna(value):
        return 0
    text = str(value).strip()
    text = text.strip('{}')
    if len(text) == 0:
        return 0
    # Split amenity list by quoted separators or commas
    text = text.replace('\"', '"')
    parts = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', text)
    items = [p.strip(' "') for p in parts if p.strip()]
    return len(items)


def bool_to_int(value):
    if pd.isna(value):
        return 0
    value = str(value).strip().lower()
    if value in {"t", "true", "yes", "y", "1", "checked", "on"}:
        return 1
    return 0


def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for column in ["last_review", "first_review", "host_since"]:
        if column in df.columns:
            df[column] = df[column].fillna(method="ffill")

    if "bathrooms" in df.columns:
        df["bathrooms"] = df["bathrooms"].fillna(df["bathrooms"].median())
    if "review_scores_rating" in df.columns:
        df["review_scores_rating"] = df["review_scores_rating"].fillna(0)
    if "bedrooms" in df.columns:
        df["bedrooms"] = df["bedrooms"].fillna(df["bathrooms"].median())
    if "beds" in df.columns:
        df["beds"] = df["beds"].fillna(df["bathrooms"].median())

    if "amenities" in df.columns:
        df["amenities"] = df["amenities"].apply(count_amenities)

    if "host_response_rate" in df.columns:
        df["host_response_rate"] = df["host_response_rate"].apply(parse_response_rate).fillna(0)

    for col in ["host_has_profile_pic", "host_identity_verified", "instant_bookable"]:
        if col in df.columns:
            df[col] = df[col].apply(bool_to_int)

    if "cleaning_fee" in df.columns:
        df["cleaning_fee"] = df["cleaning_fee"].fillna(False).apply(bool_to_int)

    return df


def encode_categorical_columns(x: pd.DataFrame):
    encoders = {}
    for col in x.columns:
        if x[col].dtype == object:
            x[col] = x[col].fillna("missing")
            encoder = LabelEncoder()
            x[col] = encoder.fit_transform(x[col])
            encoders[col] = encoder
    return x, encoders


def transform_row(row: dict, encoders: dict):
    row = row.copy()
    row["amenities"] = count_amenities(row.get("amenities", ""))
    row["host_response_rate"] = parse_response_rate(row.get("host_response_rate", 0))
    row["host_has_profile_pic"] = bool_to_int(row.get("host_has_profile_pic", 0))
    row["host_identity_verified"] = bool_to_int(row.get("host_identity_verified", 0))
    row["instant_bookable"] = bool_to_int(row.get("instant_bookable", 0))
    row["cleaning_fee"] = bool_to_int(row.get("cleaning_fee", 0))

    for col, encoder in encoders.items():
        if col in row:
            value = row[col]
            if isinstance(value, str):
                value = value.strip()
            if value in encoder.classes_.tolist():
                row[col] = encoder.transform([value])[0]
            else:
                if "missing" in encoder.classes_:
                    row[col] = int(encoder.transform(["missing"])[0])
                else:
                    row[col] = 0
    return row


def build_model():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    raw_df = pd.read_csv(DATA_PATH)
    raw_df = preprocess_df(raw_df)

    drop_columns = [
        "id",
        "name",
        "log_price",
        "description",
        "first_review",
        "host_since",
        "last_review",
        "neighbourhood",
        "thumbnail_url",
        "zipcode",
    ]
    x = raw_df.drop(columns=[c for c in drop_columns if c in raw_df.columns], errors="ignore")
    y = raw_df["log_price"]

    x, encoders = encode_categorical_columns(x)

    if CATBOOST_AVAILABLE:
        model = CatBoostRegressor(verbose=0, random_seed=42)
    else:
        model = RandomForestRegressor(random_state=42, n_estimators=100)

    model.fit(x, y)
    return model, encoders, x, raw_df


@st.cache_data(show_spinner=False)
def load_model_and_data():
    return build_model()


def predict_price(inputs: dict, model, encoders, x_columns):
    row = transform_row(inputs, encoders)
    prediction_df = pd.DataFrame([row], columns=x_columns)
    prediction = model.predict(prediction_df)[0]
    return prediction


def render_sidebar(encoders):
    st.sidebar.header("Predict your Airbnb price")
    st.sidebar.write("Enter listing data and estimate the nightly price.")

    property_type = st.sidebar.selectbox(
        "Property type",
        options=sorted(encoders["property_type"].classes_.tolist()),
    )
    room_type = st.sidebar.selectbox(
        "Room type",
        options=sorted(encoders["room_type"].classes_.tolist()),
    )
    bed_type = st.sidebar.selectbox(
        "Bed type",
        options=sorted(encoders["bed_type"].classes_.tolist()),
    )
    cancellation_policy = st.sidebar.selectbox(
        "Cancellation policy",
        options=sorted(encoders["cancellation_policy"].classes_.tolist()),
    )
    city = st.sidebar.selectbox(
        "City",
        options=sorted(encoders["city"].classes_.tolist()),
    )

    st.sidebar.subheader("Host profile")
    cleaning_fee = st.sidebar.checkbox("Cleaning fee charged")
    host_has_profile_pic = st.sidebar.checkbox("Host has profile picture", value=True)
    host_identity_verified = st.sidebar.checkbox("Host identity verified", value=True)
    instant_bookable = st.sidebar.checkbox("Instant bookable", value=False)
    host_response_rate = st.sidebar.slider(
        "Host response rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=80.0,
        step=1.0,
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Listing details")
    amenities = st.sidebar.slider("Amenities count", min_value=0, max_value=50, value=10, step=1)
    accommodates = st.sidebar.slider("Accommodates", min_value=1, max_value=20, value=2, step=1)
    bathrooms = st.sidebar.slider("Bathrooms", min_value=0.5, max_value=10.0, value=1.0, step=0.5)
    bedrooms = st.sidebar.slider("Bedrooms", min_value=0.0, max_value=10.0, value=1.0, step=0.5)
    beds = st.sidebar.slider("Beds", min_value=0.0, max_value=10.0, value=1.0, step=0.5)
    number_of_reviews = st.sidebar.number_input(
        "Number of reviews", min_value=0, max_value=2000, value=10, step=1
    )
    review_scores_rating = st.sidebar.slider(
        "Review score rating",
        min_value=0.0,
        max_value=100.0,
        value=90.0,
        step=1.0,
    )

    with st.sidebar.expander("Advanced settings", expanded=False):
        latitude = st.number_input("Latitude", value=40.7, format="%.6f")
        longitude = st.number_input("Longitude", value=-73.9, format="%.6f")
        st.caption("Advanced location features are optional.")

    submit_button = st.sidebar.button("Estimate price")

    inputs = {
        "property_type": property_type,
        "room_type": room_type,
        "bed_type": bed_type,
        "cancellation_policy": cancellation_policy,
        "city": city,
        "cleaning_fee": cleaning_fee,
        "host_has_profile_pic": host_has_profile_pic,
        "host_identity_verified": host_identity_verified,
        "instant_bookable": instant_bookable,
        "host_response_rate": host_response_rate,
        "amenities": amenities,
        "accommodates": accommodates,
        "bathrooms": bathrooms,
        "bedrooms": bedrooms,
        "beds": beds,
        "number_of_reviews": number_of_reviews,
        "review_scores_rating": review_scores_rating,
        "latitude": latitude,
        "longitude": longitude,
    }
    return inputs, submit_button


def main():
    st.title("Airbnb Price Prediction")
    st.markdown("### Estimate a nightly price for an Airbnb listing using model-driven predictions.")
    st.write(
        "Adjust the listing characteristics in the sidebar and press the button to see an estimate."
    )

    model, encoders, x_train, raw_df = load_model_and_data()
    x_columns = x_train.columns.tolist()
    inputs, submit_button = render_sidebar(encoders)

    if submit_button:
        log_price = predict_price(inputs, model, encoders, x_columns)
        predicted_price = np.exp(log_price)

        left, right = st.columns([2, 1])
        with left:
            st.subheader("Estimated nightly price")
            st.metric("Price (USD)", f"${predicted_price:,.2f}")
            st.write("---")
            st.write("### Prediction summary")
            st.write(f"**Log price:** {log_price:.3f}")
            st.write(f"**Estimated nightly price:** ${predicted_price:,.2f}")
            st.info("Use the sidebar to refine listing details and estimate again.")
        with right:
            st.subheader("Key listing inputs")
            st.write(f"**City:** {inputs['city']}")
            st.write(f"**Room type:** {inputs['room_type']}")
            st.write(f"**Property type:** {inputs['property_type']}")
            st.write(f"**Accommodates:** {inputs['accommodates']}")
            st.write(f"**Bathrooms:** {inputs['bathrooms']}")
            st.write(f"**Bedrooms:** {inputs['bedrooms']}")
            st.write(f"**Review score:** {inputs['review_scores_rating']}")
            st.write(f"**Number of reviews:** {inputs['number_of_reviews']}")
            st.write(f"**Instant bookable:** {'Yes' if inputs['instant_bookable'] else 'No'}")
            st.write(f"**Cleaning fee:** {'Yes' if inputs['cleaning_fee'] else 'No'}")
    else:
        st.info("Enter listing details in the sidebar and click **Estimate price** to generate a prediction.")

    with st.expander("Model and dataset details", expanded=True):
        st.write("This app trains a regression model from `Airbnb Data/Airbnb_Data.csv` using the same features as the notebook.")
        st.write(f"- Dataset rows loaded: **{raw_df.shape[0]}**")
        st.write(f"- Features used: **{len(x_columns)}**")
        st.write(f"- Model type: **{'CatBoostRegressor' if CATBOOST_AVAILABLE else 'RandomForestRegressor'}**")

    st.markdown("---")
    st.write("### Tips")
    st.write(
        "- Use realistic values for city, room type and property type. " 
        "- Higher review scores and more amenities generally increase predicted price.  "
        "- Advanced location inputs are optional and may only marginally affect the result."
    )


if __name__ == "__main__":
    main()
