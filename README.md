# eSSL-attlog
An attendance logger built on top of PyZk and reverse-engineered eSSL push APIs

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or with auto-reload for development:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

The server provides the following routers:

- **Push API** (`/`) - Handles push data from eSSL devices
- **Attendance** (`/attendance`) - Manages attendance records
- **Users** (`/users`) - Manages user data
- **Actions** (`/actions`) - Manages system actions
- **Stats** (`/stats`) - Provides statistics

Each router includes GET and POST endpoints that return dummy JSON data.

## API Documentation

Once the server is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc
- OpenAPI schema: http://localhost:8000/openapi.json
