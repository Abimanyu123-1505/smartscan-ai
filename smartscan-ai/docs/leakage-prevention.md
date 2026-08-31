# Leakage Prevention

Data leakage occurs when information from outside the training dataset is used to create the model.
To prevent this:
1. Time-series data is split strictly chronologically.
2. The pipeline enforces a hashing check on dataset identifiers to confirm mutual exclusivity of train/test splits.
3. Feature engineering is strictly isolated to the training context prior to application on validation sets.
