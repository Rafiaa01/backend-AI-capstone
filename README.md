# FlyRank Lead Capture Platform

A backend-powered embeddable lead capture widget platform built with FastAPI, SQLite, SQLAlchemy, and Inngest.

The platform allows businesses to create widgets, embed a JavaScript widget on a website, collect customer submissions, store them in a database, and process them asynchronously using Inngest.

---

## Features

- Create and manage tenants
- Create lead capture widgets
- Embeddable JavaScript widget
- Collect name, email, and message
- Honeypot spam protection
- Store submissions in SQLite
- Capture visitor IP address
- Background processing with Inngest
- Submission status tracking
- REST API with FastAPI
- Interactive API documentation with Swagger UI
- CORS support for embedded widgets

---

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Inngest
- JavaScript
- HTML
- CSS

---

## Project Structure

```text
flyrank-capstone-widget-platform/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── functions.py
│   └── inngest_client.py
│
├── static/
│   └── widget.js
│
├── customer-site/
│   ├── index.html
│   └── style.css
│
├── tests/
│   └── index.html
│
├── flyrank.db
├── requirements.txt
├── .env.example
├── DESIGN.md
├── BUILDLOG.md
├── EVIDENCE.md
└── README.md