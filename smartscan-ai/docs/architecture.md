# Architecture

Our architecture is segmented into decoupled microservices and independent modules to foster scalability and research reproducibility:

1. **Data Ingestion Module**: Safely imports raw RF traces and validates format.
2. **Preprocessing Pipeline**: Converts and standardizes data to PyArrow/Parquet files.
3. **Inference Engine**: Executes ML models for anomaly and signature detection.
4. **Simulation Scheduler**: Dynamically maps detection outputs to abstract channel assignments (F1..FN) while strictly avoiding hardware execution.
5. **Evaluation Subsystem**: Collects logging and metrics to report on pipeline accuracy.
6. **Dashboard Interface**: Provides visualization for system operators.
