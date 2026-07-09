# AdTech Bid Workflow Demo Platform Spec

## 1. Project Summary

Build a full-fledged demo adTech platform focused on the SSP-side bid request workflow.

The platform should demonstrate:

- authentication and authorization
- campaign and inventory management
- bid request simulation
- auction eligibility and winner selection
- impression, click, and conversion event tracking
- analytics dashboard
- an agentic AI copilot for explanation and operational insights

This project is intended for interview demonstration, so the implementation should prioritize:

- clear architecture
- realistic workflow
- clean UI
- explainable business logic
- fast local setup
- stable demo behavior

## 2. Demo Goal

The core demo should show this sequence end to end:

1. A user logs into the platform.
2. The user views or manages campaigns and placements.
3. The user submits a simulated bid request.
4. The system evaluates campaign eligibility.
5. The auction engine selects a winner or returns no-bid.
6. The user logs or triggers impression, click, and conversion events.
7. The dashboard updates with new metrics.
8. The AI copilot explains why the auction result happened and what insights matter.

## 3. Product Scope

### In Scope

- user login/logout
- role-based access control
- campaign CRUD
- publisher and placement CRUD
- bid request simulation
- auction trace inspection
- event ingestion for impression, click, conversion
- dashboard metrics and charts
- AI copilot for workflow and analytics explanation

### Out of Scope

- external SSP/DSP integrations
- real-time distributed streaming
- production-grade SSO or MFA
- advanced attribution windows
- ML-based bid optimization
- multi-tenant billing

## 4. Lightweight Demo Stack

Use the following implementation stack:

- Python
- FastAPI for backend APIs
- Streamlit for web UI
- SQLite for persistence
- SQLAlchemy for ORM/data access
- Pydantic for API and domain schemas
- Polars for analytics computation
- Plotly for charts
- JWT authentication
- passlib/bcrypt for password hashing

## 5. Architecture Overview

The platform should use a layered architecture.

### Frontend / Experience Layer

Streamlit app with the following views:

- Login
- Home Dashboard
- Campaign Manager
- Publisher & Placement Manager
- Bid Simulator
- Auction Trace Viewer
- Event Explorer
- Analytics Dashboard
- AI Copilot

### API Layer

FastAPI handles:

- authentication APIs
- campaign APIs
- publisher and placement APIs
- bid request and auction APIs
- event APIs
- metrics APIs
- copilot APIs

### Domain Layer

Core services:

- Auth Service
- User Service
- Campaign Service
- Inventory Service
- Bid Request Service
- Eligibility Service
- Auction Service
- Frequency Cap Service
- Event Service
- Metrics Service
- Copilot Service

### Storage Layer

SQLite tables for:

- users
- campaigns
- publishers
- placements
- bid_requests
- auction_decisions
- auction_candidates
- impression_events
- click_events
- conversion_events

### Analytics Layer

Polars computes:

- bid request counts
- win rate
- no-bid rate
- impressions
- clicks
- conversions
- CTR
- CVR
- revenue
- campaign performance
- publisher performance
- no-bid reason breakdown
- geo/device splits

## 6. Roles and Permissions

### Roles

- admin
- adops
- analyst
- viewer

### Permissions

#### admin

- manage users
- manage campaigns
- manage publishers and placements
- run bid simulations
- log events
- view analytics
- use copilot

#### adops

- manage campaigns
- manage publishers and placements
- run bid simulations
- log events
- view analytics
- use copilot

#### analyst

- view dashboard
- view auction traces
- view events
- use copilot

#### viewer

- view dashboard
- view auction traces

## 7. Main Workflow

### Bid Request Workflow

Input fields:

- publisher_id
- placement_id
- country
- device_type
- user_id
- timestamp

Execution:

1. Authenticate the current platform user.
2. Authorize the action based on role.
3. Validate the bid request payload.
4. Store the bid request.
5. Load active campaigns.
6. Evaluate campaign eligibility by:
   - status
   - country
   - device
   - placement
   - remaining budget
   - frequency cap
7. Record rejection reasons for ineligible campaigns.
8. Rank eligible campaigns by bid_cpm.
9. Select the winner or return no-bid.
10. Store the auction decision and candidate trace.
11. Return a structured response to the UI.

### Post-Auction Event Workflow

After a winning auction:

1. Log impression event.
2. Optionally log click event.
3. Optionally log conversion event.
4. Refresh analytics data.
5. Update dashboard views.
6. Enable AI copilot explanation of the results.

## 8. Business Rules

### Campaign Eligibility

A campaign is eligible only if:

- status is active
- target country matches request country
- target device matches request device
- target placement matches request placement
- remaining budget is greater than zero
- frequency cap for the user has not been reached

### Auction Winner Selection

V1 rule:

- highest eligible bid_cpm wins

### No-Bid Reasons

Supported reasons:

- inactive
- country_mismatch
- device_mismatch
- placement_mismatch
- budget_exhausted
- frequency_cap_reached
- no_eligible_campaign

## 9. Data Model

### users

- id
- email
- full_name
- password_hash
- role
- is_active
- created_at
- updated_at
- last_login_at

### campaigns

- id
- name
- advertiser_name
- status
- bid_cpm
- daily_budget
- remaining_budget
- frequency_cap
- created_by_user_id
- created_at
- updated_at

### campaign_targets

- id
- campaign_id
- country
- device_type
- placement_id

### publishers

- id
- name
- status
- created_at

### placements

- id
- publisher_id
- name
- placement_type
- status
- created_at

### bid_requests

- id
- publisher_id
- placement_id
- country
- device_type
- user_id
- created_at

### auction_decisions

- id
- bid_request_id
- winner_campaign_id
- decision_status
- clearing_price
- decision_reason
- created_at

### auction_candidates

- id
- auction_decision_id
- campaign_id
- eligibility_status
- rejection_reason
- score

### impression_events

- id
- auction_decision_id
- campaign_id
- publisher_id
- placement_id
- user_id
- revenue
- created_at

### click_events

- id
- auction_decision_id
- campaign_id
- created_at

### conversion_events

- id
- auction_decision_id
- campaign_id
- conversion_value
- created_at

## 10. API Surface

### Auth

- POST /auth/login
- POST /auth/logout
- GET /auth/me

### Users

- GET /users
- POST /users
- PATCH /users/{user_id}

### Campaigns

- GET /campaigns
- POST /campaigns
- PATCH /campaigns/{campaign_id}
- GET /campaigns/{campaign_id}

### Publishers

- GET /publishers
- POST /publishers

### Placements

- GET /placements
- POST /placements

### Bid Requests / Auctions

- POST /bid-requests
- GET /auctions
- GET /auctions/{auction_id}

### Events

- POST /events/impression
- POST /events/click
- POST /events/conversion
- GET /events

### Metrics

- GET /metrics/overview
- GET /metrics/timeseries
- GET /metrics/campaigns
- GET /metrics/publishers
- GET /metrics/no-bid-reasons

### Copilot

- POST /copilot/query
- GET /copilot/suggested-questions

## 11. UI Pages

### Login

- email/password login
- auth error states

### Home

- KPI cards
- recent auctions
- recent events
- quick actions

### Campaign Manager

- list campaigns
- create campaign
- edit campaign
- activate/pause campaign

### Publisher & Placement Manager

- list publishers
- create publisher
- create placement

### Bid Simulator

- create bid request form
- submit request
- show eligible campaigns
- show rejected campaigns with reasons
- show winner or no-bid result

### Auction Trace Viewer

- list recent auctions
- inspect decision details

### Event Explorer

- list impression/click/conversion events
- filter by campaign, auction, publisher

### Analytics Dashboard

- overview metrics
- time-series charts
- campaign table
- publisher table
- no-bid breakdown

### AI Copilot

- free-text question box
- suggested prompts
- generated insight response

## 12. Agentic AI Development Workflow

This project will be developed using Codex in VS Code with spec-driven development.

### Working Rules

- Always read this spec before implementing new features.
- Break work into small vertical slices.
- Implement one module at a time.
- Add tests for every service or endpoint slice.
- Compare implementation back to this spec after each feature.
- Prefer stable, demo-ready behavior over extra complexity.

### Preferred Build Order

1. project skeleton
2. database setup
3. auth models and login flow
4. RBAC enforcement
5. campaign and inventory CRUD
6. bid request endpoint
7. eligibility and auction engine
8. auction trace storage
9. event logging
10. metrics aggregation
11. dashboard pages
12. copilot insight flow

### Codex Task Pattern

Use prompts like:

- "Read spec.md and implement only the auth models, auth routes, and JWT utilities."
- "Read spec.md and implement campaign CRUD with SQLAlchemy models, Pydantic schemas, and FastAPI routes."
- "Read spec.md and implement the bid request workflow and auction selection logic with tests."
- "Compare the current implementation with spec.md and list missing requirements for the bid workflow."

## 13. Initial Folder Structure

```text
apps/
  api/
    routes/
    auth/
  web/
    pages/

core/
  domain/
    models/
    services/
  workflows/
  auth/
  permissions/

infra/
  db/
  repositories/

analytics/
  metrics/
  views/

data/
  seed/

tests/
work/
outputs/
```

## 14. Seed Data Requirements

Seed the demo with:

- 4 users across roles
- 3 publishers
- 4 placements
- 5 campaigns with mixed targeting and bid prices

Ensure seed data supports:

- one winning auction path
- one no-bid path
- one device mismatch case
- one budget exhausted case
- one frequency cap case

## 15. Acceptance Criteria

The demo is considered ready when:

- users can log in and log out
- roles visibly affect access
- campaigns and placements can be managed
- a simulated bid request can be submitted
- the system shows eligible and rejected campaigns
- a winner or no-bid response is returned with explanation
- impression, click, and conversion events can be recorded
- dashboard metrics update correctly
- the AI copilot can explain the auction result and summary metrics

## 16. Presentation Notes

When presenting the demo:

- explain that the implementation uses a lightweight local stack for speed and reliability
- map SQLite to Postgres
- map local event storage to MinIO-like raw event storage
- map Polars analytics to Druid/Trino-style analytical processing
- map frequency-cap checks to Aerospike-style low-latency state in production
- emphasize that the same workflow architecture can scale to the larger production stack
