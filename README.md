# PhishLens: Streamlit UI

AI-based phishing URL detection (UCI PhiUSIIL dataset, Logistic Regression / Decision Tree / Random Forest).

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```
Keep the folders next to `app.py`: `saved_model/`, `ML_results/`, `EDA_images/`, `assets/`.

## Pages
- **Scan**: one URL or a batch (up to 200), verdict, probability, risk scale, URL breakdown, top drivers, URL checks, CSV export
- **Overview**: scan activity, verdict split, dataset and model snapshot, EDA figures
- **Model performance**: scores by feature setting, confusion matrices, feature reliance, training plots
- **History**: searchable, filterable, exportable; saved in each visitor's own browser (localStorage), so it survives refreshes and is private per visitor; CSV export

## How scanning works
The full model needs 50 features, 29 of which come from the page itself, so a typed URL cannot feed it.
The scanner therefore uses `phishing_model_url_only_pipeline.joblib` (21 features computed from the URL string in `phishlens/engine.py`). The current file is a Random Forest trained on the large dataset (235,468 URLs); if you retrain and a different model wins, the app adapts (score explanations use coefficients for linear models and a feature-by-feature test for tree models).
`TLDLegitimateProb` and `URLCharProb` come from lookup tables built from your cleaned dataset (`python tools/build_assets.py <csv>`).
With the rebuilt features, the model agrees with the dataset labels on 99.45% of a random sample of dataset URLs, against 99.48% using the dataset's own feature values (the lookup tables were built from the same data, so this is an in-sample check).

## Known limit (worth stating in the report)
Every legitimate URL in the training data is a bare `https://www.` homepage. The model learned that pattern, so deep links
(`github.com/user/repo`, `google.com` without `www`) or hosts without `www` can score as phishing. The app marks those scans "Low reliability".
Fixing this needs more varied legitimate URLs in training.
