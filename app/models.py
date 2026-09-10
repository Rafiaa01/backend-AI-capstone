from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

from app.database import Base


# =========================================================
# TENANT
# =========================================================

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )


# =========================================================
# WIDGET
# =========================================================

class Widget(Base):
    __tablename__ = "widgets"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    tenant_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    widget_type = Column(
        String(50),
        nullable=False,
        default="signup",
    )


# =========================================================
# SUBMISSION
# =========================================================

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    widget_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    tenant_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(255),
        nullable=False,
    )

    message = Column(
        Text,
        nullable=True,
    )

    ip_address = Column(
        String(45),
        nullable=True,
    )

    country = Column(
        String(100),
        nullable=True,
    )

    city = Column(
        String(100),
        nullable=True,
    )

    # -----------------------------------------------------
    # Processing Status
    # -----------------------------------------------------

    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )

    processed_at = Column(
        DateTime,
        nullable=True,
    )

    # -----------------------------------------------------
    # Created Timestamp
    # -----------------------------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )
