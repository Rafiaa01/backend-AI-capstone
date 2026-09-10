# FlyRank Lead Capture Platform — Build Log

## Project Overview

FlyRank is an embeddable lead-capture platform that allows websites to integrate a JavaScript widget for collecting visitor information.

The platform stores submissions in a database and uses Inngest for asynchronous background processing.

---

## Phase 1 — Project Setup

### Completed

- Created FlyRank project repository
- Created Python virtual environment
- Configured FastAPI application
- Configured Uvicorn development server
- Created project structure
- Added dependency management through `requirements.txt`

### Technologies

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Inngest
- JavaScript
- HTML/CSS

---

## Phase 2 — Database

### Completed

Implemented SQLAlchemy database models:

- Tenant
- Widget
- Submission

The application uses SQLite during development.

Database file:

```text
flyrank.db