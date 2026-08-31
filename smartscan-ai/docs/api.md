# API Documentation

The backend exposes several REST endpoints:

- `GET /health`: Health check for the service.
- `POST /ingest`: Upload data for processing.
- `GET /metrics`: Fetch latest system performance metrics.
- `POST /schedule`: Trigger a simulation scheduling event and receive the updated F1..FN allocation matrix.

For detailed schema definitions, navigate to `http://localhost:8001/docs` when the backend is running to access the FastAPI Swagger UI.
