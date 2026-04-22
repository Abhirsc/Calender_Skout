# Smart Calendar App Build

Minimal, elegant, cross-device smart calendar MVP with a FastAPI backend and React frontend. The app is designed for dark mode by default, with a mobile-first layout that also works cleanly on desktop.

## What is included

- FastAPI backend with SQLModel models and SQLite storage
- React + Vite frontend with month, week, and agenda views
- Source toggles for work, personal, public, and conferences layers
- Manual event creation for all calendar layers
- Seed data for editable source records and example events
- ICS ingestion service and weekly APScheduler scan hook
- ICS file upload for creating new calendar feed sources
- Save, pin, notes, and Slack webhook payload support
- Docker and docker-compose starter setup
- Basic tests for deduplication, relevance scoring, save/pin flow, and Slack payload generation
- Optional shared-password lock for public deployments

## Stack

- Python 3.12
- FastAPI
- SQLModel / SQLAlchemy
- SQLite
- APScheduler
- React + Vite + TypeScript
- Docker

## Project structure

```text
app/
  api/
  core/
  db/
  integrations/
  models/
  schemas/
  services/
  tasks/
frontend/
  src/
tests/
```

## Quick start

1. Copy `.env.example` to `.env` and adjust values if needed.
   If you want a lightweight shared password lock, set `PUBLIC_APP_PASSWORD`.
2. Create a Python virtual environment and install backend dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

3. Start the backend:

```bash
uvicorn app.main:app --reload
```

4. In another terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

5. Open:

- API: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Docker

Run the stack with:

```bash
docker compose up --build
```

## MVP scope currently implemented

- Unified event API and seed dataset
- Public ICS parsing with embedded seed feed examples
- Smart scan criteria persistence
- Save and pin workflow with inline notes
- Slack payload generation and optional webhook delivery
- Responsive dark calendar dashboard and admin pages
- Weekly public/conference scan status visible in settings
- Optional shared-password unlock flow backed by the API
- Scanned events can be added directly into the in-app calendar, with ICS download kept as a secondary option

## Planned next implementation steps

- Complete live Outlook Microsoft Graph sync
- Add remote ICS fetching and caching
- Expand deduplication with similarity thresholds
- Improve calendar layout density for heavier event loads
- Add authentication and per-user settings

## Shared password lock

For a simple public-facing gate, add this to `.env`:

```bash
PUBLIC_APP_PASSWORD=choose-a-shared-password
```

This is an MVP-style shared lock, not full user authentication.

## Testing

Once dependencies are installed:

```bash
pytest
```

## Seeded source placeholders

Editable seed source records include:

- Work Outlook
- Personal Apple
- Ecology Societies Feed
- Landcare Groups
- Biodiversity Data Communities

These are starter records only and can be changed in the UI or API.

crafted with <3 by abhirsc :)
