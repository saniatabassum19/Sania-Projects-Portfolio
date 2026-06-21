# Airbnb Price Prediction

A Streamlit app that predicts nightly Airbnb prices using a regression model trained on the included Airbnb dataset.

## Project Contents

- `streamlit_app.py` - Main Streamlit application.
- `requirements.txt` - Python dependencies.
- `Airbnb Data/Airbnb_Data.csv` - Dataset used to train the model.
- `Airbnb_Price_Prediction.ipynb` - Notebook for exploration and model analysis.
- `catboost_info/` - Training artifacts from CatBoost model runs.
- `output/` - Output folder for results or exports.

## Features

- Predicts nightly price using listing features.
- Supports `CatBoostRegressor` when `catboost` is installed; otherwise falls back to `RandomForestRegressor`.
- Preprocesses input data automatically.
- Interactive sidebar for listing configuration.
- Displays estimated price and key prediction inputs.

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

If you only want the default model path, `catboost` is optional; the app works with `scikit-learn`.

## Run the app

From the project folder, run:

```bash
streamlit run streamlit_app.py
```

Then open the local Streamlit URL shown in the terminal.

## How to use

1. Open the app in your browser.
2. Set listing values in the sidebar:
   - Property type
   - Room type
   - Bed type
   - Cancellation policy
   - City
   - Host profile and listing details
3. Click `Estimate price`.
4. Review the estimated nightly price and model summary.

## Notes

- The model trains on `Airbnb Data/Airbnb_Data.csv` when the app starts.
- The prediction output is transformed from a log price to a USD nightly price.
- Advanced latitude/longitude inputs are optional.

## License

This project is provided as-is for demonstration and experimentation.
