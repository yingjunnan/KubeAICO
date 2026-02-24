# KubeAICO

KubeAICO is a Kubernetes operations dashboard MVP with:

- FastAPI backend (`/Users/yingjunnan/Desktop/kubeaico/backend`)
- Vue 3 + Vite frontend (`/Users/yingjunnan/Desktop/kubeaico/frontend`)
- Single-cluster operations focus
- Prometheus + Kubernetes API dual data collector abstraction
- Auth, overview metrics, alert aggregation, workload operations, AI analysis task pipeline

## Implemented Scope

- Login auth (JWT) without fine-grained RBAC
- Cluster overview summary API and realtime websocket stream
- Metrics time-series API
- Resource management APIs for:
  - Deployment
  - StatefulSet
  - DaemonSet
  - Pod
  - Service
  - Ingress
- Resource detail API with related events + pod logs
- Scale and rollout-restart operations with audit log
- Alert aggregation from K8s events + Prometheus firing alerts
- AI analysis interface:
  - rule engine
  - async task workflow
  - pluggable LLM adapter placeholder
- Frontend pages:
  - Login
  - Overview dashboard
  - Resource management
  - Alerts
  - Audit logs
  - AI analysis

## Repository Structure

```text
backend/
  app/
    api/
    analyzer/
    collector/
    core/
    db/
    repository/
    schemas/
    service/
  tests/
frontend/
  src/
    components/
    router/
    services/
    stores/
    views/
```

## Quick Start (Local)

### 1) Backend

```bash
cd /Users/yingjunnan/Desktop/kubeaico/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

Default seeded account:

- username: `admin`
- password: `admin123`

### 2) Frontend

```bash
cd /Users/yingjunnan/Desktop/kubeaico/frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:5173`

### 3) Docker Compose

```bash
cd /Users/yingjunnan/Desktop/kubeaico
docker compose up --build
```

## Key API Endpoints

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/overview/summary`
- `GET /api/v1/metrics/timeseries`
- `GET /api/v1/resources/{kind}`
- `GET /api/v1/resources/{kind}/{name}/detail`
- `POST /api/v1/resources/{kind}/{name}/scale`
- `POST /api/v1/resources/{kind}/{name}/rollout-restart`
- `GET /api/v1/alerts`
- `GET /api/v1/audit/logs`
- `POST /api/v1/ai/analyze`
- `GET /api/v1/ai/tasks/{task_id}`
- `WS /ws/overview`

## Configuration

Copy examples and adjust:

- `/Users/yingjunnan/Desktop/kubeaico/backend/.env.example`
- `/Users/yingjunnan/Desktop/kubeaico/frontend/.env.example`

Set `USE_MOCK_DATA=false` and configure:

- `PROMETHEUS_URL`
- `K8S_API_URL`
- `K8S_BEARER_TOKEN`

for real cluster mode.

## Testing

Backend test files:

- `/Users/yingjunnan/Desktop/kubeaico/backend/tests/test_rules_engine.py`
- `/Users/yingjunnan/Desktop/kubeaico/backend/tests/test_api_smoke.py`

Run:

```bash
cd /Users/yingjunnan/Desktop/kubeaico/backend
python3 -m pytest -q
```

## Notes

- Collectors default to mock mode for local development.
- Redis service is included in compose for future cache/stream extension.
- Current auth model is account-based login only (no RBAC).
