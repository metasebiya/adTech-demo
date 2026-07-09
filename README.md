# AdTech Bid Workflow Demo Platform

Lightweight demo adTech platform focused on the SSP-side bid request workflow, built from `spec.md` using FastAPI, Streamlit, SQLite, SQLAlchemy, Pydantic, Polars, Plotly, and JWT auth.

## Current Slice

The project currently includes:

- project scaffold aligned to `spec.md`
- SQLite-backed FastAPI backend
- JWT-based login flow
- protected `GET /auth/me`
- RBAC enforcement for inventory management
- publisher and placement CRUD APIs
- campaign CRUD with placement-based targeting
- bid request simulation with eligibility checks and auction trace storage
- impression, click, and conversion event ingestion plus event listing
- Streamlit login page, inventory manager, and campaign manager
- backend auth, inventory, campaign, auction, and event tests
- Docker-based local runtime
- GitHub Actions CI for tests and image builds

## Local Run

### Option 1: Docker Compose

```bash
docker compose up --build
```

App URLs:

- API: `http://localhost:8000`
- API health: `http://localhost:8000/health`
- Streamlit UI: `http://localhost:8501`

Default seeded demo users all use password `ChangeMe123!`:

- `admin@adtech-demo.local`
- `adops@adtech-demo.local`
- `analyst@adtech-demo.local`
- `viewer@adtech-demo.local`

### Option 2: Run Locally Without Containers

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn apps.api.main:app --reload
```

Start Streamlit in another terminal:

```bash
streamlit run apps/web/app.py
```

## Test

```bash
pytest -q
```

## CI

GitHub Actions workflow: `.github/workflows/ci.yml`

It currently:

- installs Python dependencies
- runs the auth test suite
- builds API and Streamlit container images

## Notes

- The workflow is CI-focused for now because the spec does not yet define a deployment target.
- SQLite is persisted locally through the `data/` directory when running with Docker Compose.
