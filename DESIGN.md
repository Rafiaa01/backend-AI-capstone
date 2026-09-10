# FlyRank Lead Capture Platform — Design

## 1. Problem

FlyRank provides embeddable lead-capture widgets that customers can place on
websites they do not control. A customer creates and manages widgets through
an authenticated API. A visitor interacts with the widget on an external
website, and the submitted lead is validated and stored against the correct
customer and widget.

The system is designed as a multi-tenant backend. Customer data must remain
isolated so one tenant can never access another tenant's widgets or
submissions.

---

## 2. Data Model

### Tenant

Represents one customer/account.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| name | string | Customer name |
| created_at | timestamp | Creation time |

### Widget

Represents an embeddable lead-capture widget owned by a tenant.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| tenant_id | UUID | Foreign key to Tenant |
| type | string | signup_form, CTA, or popover |
| title | string | Widget title |
| description | string | Optional description |
| fields | JSON | Form field definitions |
| button_text | string | Submit button text |
| display_options | JSON | Display configuration |
| version | integer | Incremented when widget config changes |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Last update |

Indexes:

- `(tenant_id, id)` for tenant-scoped widget lookup.
- `(tenant_id, created_at)` for tenant dashboard/listing queries.

### Submission

Represents one visitor submission.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| tenant_id | UUID | Owning tenant |
| widget_id | UUID | Source widget |
| payload | JSON | Validated submitted fields |
| ip_address | string | Visitor IP |
| country | string | Optional geo enrichment |
| city | string | Optional geo enrichment |
| user_agent | string | Visitor browser information |
| created_at | timestamp | Submission time |

Indexes:

- `(tenant_id, created_at)` for dashboard queries.
- `(tenant_id, widget_id, created_at)` for per-widget submission queries.

Every submission is linked to both `tenant_id` and `widget_id`.
Tenant filtering is enforced in backend queries, not only in the UI.

---

## 3. Tenant Isolation

Authenticated requests identify the current tenant from the authenticated
user/session.

Every widget-management and dashboard query is scoped by `tenant_id`.

A tenant cannot:

- read another tenant's widgets;
- update or delete another tenant's widgets;
- read another tenant's submissions;
- access another tenant's dashboard statistics.

Public submission requests identify the widget, and the server resolves the
owning tenant from the trusted widget record rather than trusting a
client-supplied tenant ID.

---

## 4. Embed Flow

The customer receives a widget-specific embed snippet:

    <script src="http://localhost:8000/widget.js?id=abc123"></script>

The flow is:

    Customer Website
          |
          | 1. Load widget.js
          v
    Versioned Widget Bundle
          |
          | 2. GET /widgets/{id}/config
          v
    Public Widget Config
          |
          | 3. Render form
          v
    Visitor enters data
          |
          | 4. POST /submissions
          v
    Validate -> Rate Limit -> Spam Check
          |
          v
    Geo Enrichment
      A -> B -> no geo
          |
          v
    Store Submission
          |
          v
    Optional Email/Webhook Side Effect

The widget configuration is small and cached. The JavaScript bundle is
versioned so browsers can cache it for a long period while releases can use
a new version.

---

## 5. API Contracts

### A. Authenticated Widget Management API

These endpoints are used by the widget owner.

    POST   /widgets
    GET    /widgets
    GET    /widgets/{widget_id}
    PATCH  /widgets/{widget_id}
    DELETE /widgets/{widget_id}

Authentication is required.

Example create request:

    {
      "type": "signup_form",
      "title": "Get in touch",
      "description": "Leave your details and we will contact you.",
      "fields": [
        {"name": "name", "type": "text", "required": true},
        {"name": "email", "type": "email", "required": true}
      ],
      "button_text": "Submit",
      "display_options": {}
    }

Successful creation returns `201 Created`.

Unauthorized requests return `401 Unauthorized`.

A widget belonging to another tenant must not be accessible.

---

### B. Public Widget Delivery API

Public endpoint used by the customer's website:

    GET /widgets/{widget_id}/config

Returns only the configuration required by the widget.

Example response:

    {
      "id": "abc123",
      "type": "signup_form",
      "title": "Get in touch",
      "fields": [
        {"name": "name", "type": "text", "required": true},
        {"name": "email", "type": "email", "required": true}
      ],
      "button_text": "Submit",
      "version": 1
    }

The response includes appropriate `Cache-Control` headers.

The widget JavaScript is served as a versioned asset.

---

### C. Public Submission API

Visitors submit form data through:

    POST /submissions

Example request:

    {
      "widget_id": "abc123",
      "data": {
        "name": "Jane Doe",
        "email": "jane@example.com"
      },
      "honeypot": ""
    }

Processing order:

1. Validate request size and structure.
2. Resolve the widget and tenant.
3. Apply rate limiting.
4. Check the honeypot spam field.
5. Validate submitted fields against widget configuration.
6. Attempt IP-to-geo enrichment using provider A, then provider B.
7. Store the submission.
8. Trigger non-critical email/webhook side effects.

A successful submission returns `201 Created`.

Invalid input returns a clean `4xx` JSON response.

Rate-limited requests return `429 Too Many Requests`.

Provider failures must not prevent a valid submission from being stored.

---

## 6. Layered Architecture

The application will use three main layers:

    HTTP/API Layer
        |
        v
    Business Logic / Services
        |
        v
    Data / Repository Layer
        |
        v
    PostgreSQL / SQLite

The HTTP layer handles authentication, request parsing, responses, and CORS.

The service layer handles widget rules, submission processing, rate limiting,
spam protection, enrichment, and safe side effects.

The data layer handles persistence, migrations, relationships, indexes, and
tenant-scoped queries.

---

## 7. Explicit Non-Goal

This project will NOT build a full visual form-builder or production SaaS
dashboard.

The widget UI will remain intentionally minimal. The customer test website
will be a local HTML page served from a different origin. No real CDN, custom
domain, or production hosting is required for the capstone.

The focus is backend correctness, tenant isolation, validation, resilience,
caching, CORS, and the embeddable widget flow.