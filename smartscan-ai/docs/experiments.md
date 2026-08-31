# Experiments

The `experiments/` directory (if created) tracks historical runs and their configurations.
We record:
- Random Seed used.
- Hyperparameters.
- Final Model Checkpoints.
- Metric outputs mapped against theoretical maximums.

Refer to `Makefile` targets like `make benchmark` to run automated experimental suites.
