from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

import inngest
import inngest.fast_api

from app.inngest_client import inngest_client
from app.functions import process_lead, process_submission
from app.database import engine, Base, get_db
from app import models


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="FlyRank Lead Capture Platform",
    description="Embeddable Widget & Lead-Capture Platform",
    version="0.1.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# STATIC / WIDGET FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


@app.get("/widget.js")
def get_widget():
    return FileResponse(
        "static/widget.js",
        media_type="application/javascript",
    )


# =========================================================
# REQUEST MODELS
# =========================================================

class Lead(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    email: EmailStr

    message: str | None = Field(
        default=None,
        max_length=2000,
    )


class SubmissionRequest(BaseModel):
    widget_id: int

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    email: EmailStr

    message: str | None = Field(
        default=None,
        max_length=2000,
    )

    honeypot: str | None = Field(
        default=None,
        max_length=100,
    )


# =========================================================
# BASIC ROUTES
# =========================================================

@app.get("/")
def root():
    return {
        "message": "FlyRank Lead Capture Platform API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================================================
# TEST LEAD ENDPOINT
# =========================================================

@app.post("/leads", status_code=202)
async def create_lead(lead: Lead):

    await inngest_client.send(
        inngest.Event(
            name="lead/created",
            data={
                "lead_id": str(lead.email),
                "name": lead.name,
                "email": str(lead.email),
                "message": lead.message,
            },
        )
    )

    return {
        "message": "Lead accepted for processing",
        "lead_id": str(lead.email),
        "event": "lead/created",
    }


# =========================================================
# CREATE WIDGET
# =========================================================

class WidgetRequest(BaseModel):
    tenant_id: int
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )
    widget_type: str = Field(
        default="signup",
        max_length=50,
    )


@app.post("/widgets", status_code=201)
def create_widget(
    widget_data: WidgetRequest,
    db: Session = Depends(get_db),
):

    widget = models.Widget(
        tenant_id=widget_data.tenant_id,
        name=widget_data.name,
        widget_type=widget_data.widget_type,
    )

    db.add(widget)
    db.commit()
    db.refresh(widget)

    return {
        "id": widget.id,
        "tenant_id": widget.tenant_id,
        "name": widget.name,
        "widget_type": widget.widget_type,
    }


# =========================================================
# GET ALL WIDGETS
# =========================================================

@app.get("/widgets")
def get_widgets(
    db: Session = Depends(get_db),
):

    widgets = (
        db.query(models.Widget)
        .order_by(models.Widget.id.asc())
        .all()
    )

    return [
        {
            "id": widget.id,
            "tenant_id": widget.tenant_id,
            "name": widget.name,
            "widget_type": widget.widget_type,
        }
        for widget in widgets
    ]


# =========================================================
# GET SINGLE WIDGET
# =========================================================

@app.get("/widgets/{widget_id}")
def get_widget_by_id(
    widget_id: int,
    db: Session = Depends(get_db),
):

    widget = (
        db.query(models.Widget)
        .filter(
            models.Widget.id == widget_id
        )
        .first()
    )

    if not widget:
        return {
            "message": "Widget not found"
        }

    return {
        "id": widget.id,
        "tenant_id": widget.tenant_id,
        "name": widget.name,
        "widget_type": widget.widget_type,
    }


# =========================================================
# PUBLIC SUBMISSION ENDPOINT
# =========================================================

@app.post("/submissions", status_code=201)
async def create_submission(
    submission: SubmissionRequest,
    request: Request,
    db: Session = Depends(get_db),
):

    # -----------------------------------------------------
    # Honeypot Spam Protection
    # -----------------------------------------------------

    if submission.honeypot:
        return {
            "message": "Submission rejected"
        }

    # -----------------------------------------------------
    # Find Widget
    # -----------------------------------------------------

    widget = (
        db.query(models.Widget)
        .filter(
            models.Widget.id == submission.widget_id
        )
        .first()
    )

    if not widget:
        return {
            "message": "Widget not found"
        }

    # -----------------------------------------------------
    # Get Visitor IP
    # -----------------------------------------------------

    client_ip = (
        request.client.host
        if request.client
        else None
    )

    # -----------------------------------------------------
    # Create Submission
    # -----------------------------------------------------

    new_submission = models.Submission(
        widget_id=widget.id,
        tenant_id=widget.tenant_id,
        name=submission.name,
        email=str(submission.email),
        message=submission.message,
        ip_address=client_ip,
    )

    # -----------------------------------------------------
    # Save Submission
    # -----------------------------------------------------

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    # -----------------------------------------------------
    # Send Inngest Event
    # -----------------------------------------------------

    await inngest_client.send(
        inngest.Event(
            name="submission/created",
            data={
                "submission_id": new_submission.id,
                "widget_id": widget.id,
                "tenant_id": widget.tenant_id,
                "name": submission.name,
                "email": str(submission.email),
            },
        )
    )

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "message": "Submission stored successfully",
        "submission_id": new_submission.id,
        "status": new_submission.status,
        "event": "submission/created",
    }


# =========================================================
# GET ALL SUBMISSIONS
# =========================================================

@app.get("/submissions")
def get_submissions(
    db: Session = Depends(get_db),
):

    submissions = (
        db.query(models.Submission)
        .order_by(models.Submission.id.desc())
        .all()
    )

    return [
        {
            "id": submission.id,
            "widget_id": submission.widget_id,
            "tenant_id": submission.tenant_id,
            "name": submission.name,
            "email": submission.email,
            "message": submission.message,
            "status": submission.status,
            "processed_at": (
                submission.processed_at.isoformat()
                if submission.processed_at
                else None
            ),
            "created_at": (
                submission.created_at.isoformat()
                if submission.created_at
                else None
            ),
        }
        for submission in submissions
    ]


# =========================================================
# GET SINGLE SUBMISSION
# =========================================================

@app.get("/submissions/{submission_id}")
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
):

    submission = (
        db.query(models.Submission)
        .filter(
            models.Submission.id == submission_id
        )
        .first()
    )

    if not submission:
        return {
            "message": "Submission not found"
        }

    return {
        "id": submission.id,
        "widget_id": submission.widget_id,
        "tenant_id": submission.tenant_id,
        "name": submission.name,
        "email": submission.email,
        "message": submission.message,
        "status": submission.status,
        "processed_at": (
            submission.processed_at.isoformat()
            if submission.processed_at
            else None
        ),
        "created_at": (
            submission.created_at.isoformat()
            if submission.created_at
            else None
        ),
    }


# =========================================================
# TEST PAGE
# =========================================================

@app.get("/test")
def test_page():
    return FileResponse(
        "tests/index.html"
    )


# =========================================================
# INNGEST SERVE ENDPOINT
# =========================================================

inngest.fast_api.serve(
    app,
    inngest_client,
    [
        process_lead,
        process_submission,
    ],
)