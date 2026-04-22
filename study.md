# Study Guide: Smart Calendar App Build

## Purpose

This file explains the project in a learning-friendly way so the setup, theory, and workflow stay easy to understand.

## What this project is

`Calender_Skout` is the workspace for a smart calendar application. The idea is to build a product that can help users manage events, schedules, reminders, and intelligent planning features.

## How to use this project at the start

1. Keep project notes updated in `memo.txt`.
2. Keep dependencies, bugs, and tests recorded in `dependency.txt`.
3. Use this file to understand the system before adding code.
4. Start with planning, then choose a tech stack, then build in small steps.

## How this starter codebase is organised

### Backend flow

- `app/main.py` starts FastAPI, creates tables, seeds the database, and starts the weekly scheduler.
- `app/api/` contains HTTP routes for events, settings, sources, Slack settings, and manual scans.
- `app/models/` stores database models for sources, external events, saved events, notes, criteria, scan runs, and Slack settings.
- `app/services/` contains business logic such as ICS parsing, deduplication, relevance scoring, save/pin workflow, and Slack payload generation.
- `app/tasks/` contains scheduled job setup.
- `app/integrations/` is where provider-specific logic lives, such as Microsoft Outlook.

### Frontend flow

- `frontend/src/pages/` contains the main screens: calendar, saved events, sources, and settings.
- `frontend/src/components/` contains reusable UI pieces such as the legend, month grid, week list, and event drawer.
- `frontend/src/lib/api.ts` keeps API calls in one place so the UI stays simpler.
- `frontend/src/styles/app.css` defines the dark visual system and responsive layout.

## Theory behind the chosen architecture

### Why FastAPI

- FastAPI is a good MVP backend because it is readable, type-hint friendly, and fast to develop.
- It makes it easy to expose JSON APIs for a React frontend.
- It works well with Pydantic-based validation and SQLModel.

### Why SQLModel and SQLite

- SQLModel keeps model definitions beginner-readable.
- SQLite is ideal for a single-user MVP because setup is minimal.
- The data model can later move to PostgreSQL with only moderate refactoring.

### Why service-layer separation

- Integrations change more often than core business logic.
- Keeping `services/` separate from `integrations/` helps us swap feed providers later.
- This separation also makes testing simpler.

### Why React + Vite

- React gives flexible UI composition for calendar views and panels.
- Vite keeps the frontend fast to start and simple to develop.
- A web app first approach makes iPhone Safari and desktop support easier to manage than separate native apps.

## Core theory behind the app

### 1. Calendar domain basics

A calendar app usually manages:

- events
- dates and times
- reminders
- recurring schedules
- attendees
- notifications

Important theory:

- Time zones matter because a date and time can mean different local times in different places.
- Recurring events are more complex than one-time events because rules must be stored correctly.
- Reminders and notifications often depend on background jobs or scheduled services.

### 2. Smart features

A smart calendar app may include:

- automatic event suggestions
- schedule conflict detection
- reminder optimization
- natural language event creation
- prioritization of important tasks

Important theory:

- Smart behavior usually comes from rules, AI prompts, or machine learning.
- A simple version can begin with rule-based logic before adding advanced AI features.

### 3. Product-building process

A strong workflow is:

1. Define user problems.
2. Decide the first small version to build.
3. Pick the stack.
4. Set up the codebase.
5. Build features one by one.
6. Test each feature.
7. Record learnings and bugs.

## Current MVP implementation theory

### Unified event schema

All external feeds are normalized into a single `ExternalEvent` model. This matters because:

- the UI should not need to care whether an event came from Outlook, Apple, or a public ICS feed
- filters and deduplication work better when the data shape is consistent
- future ranking or AI enrichment becomes easier

### Relevance scoring

The first scoring pass is intentionally simple:

- keyword matching
- preferred organisation matching
- preferred location matching
- event type matching
- date horizon weighting
- source weighting

This is enough for MVP discovery and creates a clean base for later semantic search or embeddings.

### Weekly scanning

The scheduled scan is separated from the user interface because event discovery is background work.
That means:

- the app can refresh opportunity sources automatically
- scan history can be shown in the UI
- later we can move scanning from local scheduler to a hosted worker without changing the whole app

## Good first milestones

- Create the repository and project structure.
- Choose frontend, backend, and database tools.
- Define the first feature set.
- Build a basic event creation flow.
- Add event listing and calendar view.

## Event deletion theory

- Deleting an event is not only about removing one row from `external_events`.
- If the event has been saved or annotated, related rows in `saved_events` and `event_notes` must also be removed.
- Handling that cleanup in the API keeps the UI simple and prevents orphaned records in SQLite.
- A safe MVP delete flow is:
  - confirm intent in the UI
  - call a single backend delete endpoint
  - refresh the event lists after the server confirms deletion

## Difference between delete, unsave, and dismiss

- `Delete event` removes the event itself from the unified calendar.
- `Remove from saved` keeps the event in the calendar but removes the saved decision and attached notes.
- `Not interested` currently removes a scanned suggestion from the calendar store so it no longer appears in the review panel.

This distinction matters because these actions serve different user intentions:

- delete when the record should be gone
- unsave when the event can stay but your notes/bookmark should go
- dismiss when a suggestion is not useful and should leave the review queue

## Learning approach for this project

- Start simple and keep the first version small.
- Learn the domain before adding complexity.
- Record every major decision so future changes are easier.
- Prefer steady progress over perfect design.
