# 🪪 eSSL Attendance Server 

An unofficial server for receiving and storing attendance logs and user data from eSSL/ZkTeco biometric devices. Based on reverse-engineered implementations of the ADMS protocol ie. the push APIs and PyZk library.

This server saves data into JSON files and provides REST API endpoints to access and manage the data.

## 🚀 Getting Started

### 🐍 via Python

Ensure you are in a Python 3.8+ environment. Ideally, a virtual environment.

1. Clone the repository:
```bash
git clone https://github.com/ELT-Global/eSSL-attlog.git
cd eSSL-attlog
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000

# Or with auto-reload for development:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 🐬 via Docker

1. Build the Docker image:
```bash
docker build -t essl-attlog-server .
```

2. Run the Docker container:
```bash
docker run -d -p 8000:8000 --name essl-attlog-server essl-attlog-server
```

### ☁️ via Coolify

This repository is pre-configured for seamless deployment on Coolify:

1. **Create a new resource** in your Coolify instance
2. **Select "Public Repository"** and enter: `https://github.com/ELT-Global/eSSL-attlog.git`
3. **Configure the deployment:**
   - **Build Pack:** Nixpacks (auto-detected)
   - **Port:** 8000 (auto-configured)
   - **Health Check:** `/health` (pre-configured)
4. **Optional - Persistent Data:** Add a volume mount in Coolify:
   - **Source:** `/data`
   - **Destination:** `/app/data`
   - This ensures your attendance data persists across deployments
5. **Deploy!** 🚀

The application will automatically:

- Install Python dependencies
- Initialize data files
- Start the FastAPI server
- Be accessible via your Coolify domain

**Note:** No additional configuration needed - everything is pre-configured via `nixpacks.toml` and `Procfile`.

## 📖 API Documentation

Since FastAPI is used, interactive API documentation is automagically generated. Once the server is running, you can access the following routes to view the OpenAPI/Redoc documentation:

- **Interactive API docs:** <http://localhost:8000/docs>
- **Alternative API docs:** <http://localhost:8000/redoc>
- **OpenAPI schema:** <http://localhost:8000/openapi.json>
