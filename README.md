# FlyRank Lead Capture Platform

A backend-powered, embeddable lead capture platform built with **FastAPI, SQLAlchemy, SQLite, Inngest, and JavaScript**.

The platform enables businesses to create lead-capture widgets, embed them on external websites, collect customer submissions, store leads securely, and process submissions asynchronously using **Inngest background functions**.

---

## 🚀 Overview

The FlyRank Lead Capture Platform provides a complete backend workflow for collecting and processing leads from external websites.

A business can:

1. Create a tenant.
2. Create a lead capture widget.
3. Embed the widget on a customer website.
4. Visitors submit their name, email, and message.
5. The backend validates and stores the submission.
6. A `lead/created` event is sent to Inngest.
7. Inngest processes the lead asynchronously.
8. The submission status is updated in the database.

### Architecture

```text
Customer Website
       │
       ▼
Embeddable JavaScript Widget
       │
       │ POST /leads
       ▼
FastAPI Backend
       │
       ├── Validation
       ├── Honeypot Protection
       ├── IP Capture
       └── Database Storage
              │
              ▼
          SQLite DB
              │
              ▼
       Inngest Event
       lead/created
              │
              ▼
     Background Processing
              │
              ▼
      Submission Status
```

---

## ✨ Features

### Tenant Management

* Create and manage business tenants.
* Associate widgets and leads with individual tenants.
* Support multi-tenant lead collection.

### Widget Management

* Create lead capture widgets.
* Configure widget information.
* Generate widget IDs for embedding.
* Embed widgets on external websites using JavaScript.

### Lead Capture

The widget collects:

* Name
* Email
* Message

Submissions are sent to the FastAPI backend through a REST API.

### Spam Protection

* Honeypot field to detect automated spam submissions.
* Invalid/spam submissions can be rejected before processing.

### Visitor Information

* Captures visitor IP address.
* Stores submission metadata for tracking and processing.

### Database

* SQLite database for local development.
* SQLAlchemy ORM for database operations.
* Tracks tenants, widgets, leads, and submission status.

### Asynchronous Processing

* Uses **Inngest** for event-driven background processing.
* New submissions trigger a `lead/created` event.
* Processing is handled asynchronously instead of blocking the API request.

### REST API

Built with FastAPI and includes endpoints for:

* Tenant management
* Widget management
* Lead submission
* Lead retrieval
* Submission status tracking
* Inngest event handling

### API Documentation

FastAPI automatically provides interactive API documentation through Swagger UI.

```text
/docs
```

---

## 🛠️ Tech Stack

| Technology     | Purpose                            |
| -------------- | ---------------------------------- |
| **Python**     | Backend programming language       |
| **FastAPI**    | REST API framework                 |
| **SQLAlchemy** | ORM and database management        |
| **SQLite**     | Local database                     |
| **Pydantic**   | Request/response validation        |
| **Inngest**    | Event-driven background processing |
| **JavaScript** | Embeddable widget                  |
| **HTML**       | Customer demo website              |
| **CSS**        | Widget and demo-site styling       |

---

## 📁 Project Structure

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
│
├── DESIGN.md
├── BUILDLOG.md
├── EVIDENCE.md
└── README.md
```

---

## 🔄 Lead Submission Workflow

When a visitor submits the widget:

```text
1. Visitor fills out the widget
             ↓
2. JavaScript sends POST /leads
             ↓
3. FastAPI receives the submission
             ↓
4. Pydantic validates the request
             ↓
5. Honeypot field is checked
             ↓
6. Visitor IP is captured
             ↓
7. Lead is stored in SQLite
             ↓
8. lead/created event is sent to Inngest
             ↓
9. Inngest processes the submission
             ↓
10. Submission status is updated
```

---

## 🔌 API

### Health Check

```http
GET /
```

Returns the API status.

### Create Lead

```http
POST /leads
```

Example request:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "I would like to learn more about your services."
}
```

The endpoint validates the submission, stores the lead, and triggers asynchronous processing.

### Inngest Endpoint

```http
/api/inngest
```

This endpoint is used by Inngest to discover and execute registered background functions.

---

## ⚡ Inngest Processing

The platform uses an event-driven workflow.

When a new lead is created, the backend sends:

```text
lead/created
```

The Inngest function:

```text
process-lead
```

receives the event and performs background processing.

This keeps the lead submission API responsive while allowing additional processing to happen asynchronously.

---

## 🛡️ Security & Reliability

The platform includes several protections:

### Honeypot Spam Protection

A hidden form field is used to identify basic automated spam submissions.

```text
Real visitor → leaves hidden field empty
Bot → may automatically fill hidden field
```

### Input Validation

Pydantic models validate incoming request data before it reaches the application logic.

### CORS

CORS support allows the widget to communicate with the backend when embedded on external websites.

### IP Capture

The visitor's IP address is captured with the submission for basic request tracking.

---

## 🧪 Testing

The project includes a test/demo directory:

```text
tests/
└── index.html
```

The customer-site can also be used to manually test the complete widget workflow.

Testing should cover:

* Valid lead submission
* Missing required fields
* Invalid email addresses
* Honeypot spam submissions
* Database persistence
* Inngest event triggering
* Submission status updates
* CORS behavior

---

## ▶️ Running Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd flyrank-capstone-widget-platform
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Then configure the required environment variables.

### 5. Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### 6. Open Swagger UI

Visit:

```text
http://127.0.0.1:8000/docs
```

Swa
