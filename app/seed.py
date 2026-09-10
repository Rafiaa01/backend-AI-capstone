from app.database import SessionLocal
from app.models import Tenant, Widget

def seed():
    db = SessionLocal()

    try:
        # Check if demo tenant already exists
        tenant = db.query(Tenant).filter(
            Tenant.name == "Demo Tenant"
        ).first()

        if not tenant:
            tenant = Tenant(
                name="Demo Tenant"
            )

            db.add(tenant)
            db.commit()
            db.refresh(tenant)

            print(f"Created tenant: {tenant.id}")
        else:
            print(f"Tenant already exists: {tenant.id}")

        # Check if demo widget already exists
        widget = db.query(Widget).filter(
            Widget.name == "Demo Signup Widget"
        ).first()

        if not widget:
            widget = Widget(
                tenant_id=tenant.id,
                name="Demo Signup Widget",
                widget_type="signup",
            )

            db.add(widget)
            db.commit()
            db.refresh(widget)

            print(f"Created widget: {widget.id}")
        else:
            print(f"Widget already exists: {widget.id}")

        print("\nSeed completed successfully.")
        print(f"Tenant ID: {tenant.id}")
        print(f"Widget ID: {widget.id}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()