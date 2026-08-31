# Contributing to SmartScan AI

## Code Style Guidelines
- Use Black for Python formatting with an 88-character line limit.
- Ensure all functions and classes have docstrings compliant with PEP 257.
- Use type hints for all function arguments and return types.

## Pull Request Process
1. Fork the repository and create your feature branch.
2. Ensure all tests pass locally.
3. Submit a pull request detailing your changes, referencing relevant issues.
4. Two approvals are required before merging.

## Data Leakage Test Requirements
Before submitting model-related changes, run the data leakage tests to ensure that validation and test datasets do not contain any samples from the training set.

## Floating Point Metric Cross-checking
When implementing new metrics, you must provide unit tests that cross-check floating point calculations against established libraries (e.g., NumPy or SciPy) to guarantee precision.
