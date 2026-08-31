# Validation

Validation checks the robustness of the trained models.
We employ k-fold cross-validation and hold-out test sets to ensure the models generalize well to unseen abstract channel configurations.
Use `make validate` to run the validation pipeline against the current dataset in `data/processed/`.
