import asyncio
from datetime import datetime

import inngest

from app.inngest_client import inngest_client
from app.database import SessionLocal
from app import models


# =========================================================
# PROCESS LEAD
# =========================================================

@inngest_client.create_function(
    fn_id="process-lead",
    trigger=inngest.TriggerEvent(
        event="lead/created"
    ),
)
async def process_lead(ctx: inngest.Context):

    data = ctx.event.data

    lead_id = data.get("lead_id")
    name = data.get("name")
    email = data.get("email")

    print(f"Processing lead: {lead_id}")

    # Temporary simulation
    await asyncio.sleep(5)

    print(f"Lead processed: {name} - {email}")

    return {
        "lead_id": lead_id,
        "status": "completed",
    }


# =========================================================
# PROCESS SUBMISSION
# =========================================================

@inngest_client.create_function(
    fn_id="process-submission",
    trigger=inngest.TriggerEvent(
        event="submission/created"
    ),
)
async def process_submission(ctx: inngest.Context):

    data = ctx.event.data

    submission_id = data.get("submission_id")

    print(f"Processing submission: {submission_id}")

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # Find submission
        # -------------------------------------------------

        submission = (
            db.query(models.Submission)
            .filter(
                models.Submission.id == submission_id
            )
            .first()
        )

        if not submission:
            print(
                f"Submission {submission_id} not found"
            )

            return {
                "submission_id": submission_id,
                "status": "not_found",
            }

        # -------------------------------------------------
        # Mark as processing
        # -------------------------------------------------

        submission.status = "processing"

        db.commit()

        print(
            f"Submission {submission_id} is processing"
        )

        # -------------------------------------------------
        # Temporary background processing
        # -------------------------------------------------

        await asyncio.sleep(5)

        # -------------------------------------------------
        # Mark as completed
        # -------------------------------------------------

        submission.status = "completed"
        submission.processed_at = datetime.utcnow()

        db.commit()
        db.refresh(submission)

        print(
            f"Submission {submission_id} completed"
        )

        return {
            "submission_id": submission_id,
            "status": "completed",
            "processed_at": (
                submission.processed_at.isoformat()
                if submission.processed_at
                else None
            ),
        }

    except Exception as e:

        db.rollback()

        print(
            f"Error processing submission "
            f"{submission_id}: {e}"
        )

        raise

    finally:

        db.close()