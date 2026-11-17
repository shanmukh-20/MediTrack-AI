"""
database.py
Database helpers, initial setup, and sample data population for MediTrack AI.
"""

from datetime import date, timedelta, datetime, timezone
from models import db, Medicine, DoseLog

def init_db(app):
    """Initialize SQLAlchemy with the Flask app and create all tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Seed if empty
        if Medicine.query.count() == 0:
            seed_demonstration_data()


def seed_demonstration_data():
    """
    Seeds a representative set of realistic medicines and past dose logs.
    Demonstrates all statuses: Active, Expiring Soon, Low Stock, Expired.
    Provides data for reminders, adherence, and analytics.
    """
    today = date.today()

    sample_medicines = [
        Medicine(
            name="Metformin",
            generic_name="Metformin Hydrochloride",
            strength="500 mg",
            form="Tablet",
            purpose="Type 2 Diabetes Mellitus glycemic control",
            instructions="Take with meals to minimize gastrointestinal discomfort.",
            frequency="Twice Daily",
            reminder_time="08:00, 20:00",
            quantity=45,
            low_stock_threshold=10,
            start_date=today - timedelta(days=60),
            end_date=None,
            expiry_date=today + timedelta(days=365)
        ),
        Medicine(
            name="Atorvastatin",
            generic_name="Atorvastatin Calcium",
            strength="20 mg",
            form="Tablet",
            purpose="Hypercholesterolemia and lipid profile control",
            instructions="Take at night with or without food.",
            frequency="Once Daily",
            reminder_time="21:00",
            quantity=4,   # Low Stock (< threshold 5)
            low_stock_threshold=5,
            start_date=today - timedelta(days=30),
            end_date=None,
            expiry_date=today + timedelta(days=240)
        ),
        Medicine(
            name="Amoxicillin",
            generic_name="Amoxicillin Trihydrate",
            strength="500 mg",
            form="Capsule",
            purpose="Bacterial respiratory tract infection",
            instructions="Complete full prescription course as advised.",
            frequency="Twice Daily",
            reminder_time="09:00, 21:00",
            quantity=14,
            low_stock_threshold=6,
            start_date=today - timedelta(days=5),
            end_date=today + timedelta(days=5),
            expiry_date=today + timedelta(days=18)  # Expiring Soon (< 30 days)
        ),
        Medicine(
            name="Lisinopril",
            generic_name="Lisinopril Dihydrate",
            strength="10 mg",
            form="Tablet",
            purpose="Hypertension management and cardiovascular protection",
            instructions="Take once daily at the same time each morning.",
            frequency="Once Daily",
            reminder_time="08:00",
            quantity=28,
            low_stock_threshold=7,
            start_date=today - timedelta(days=45),
            end_date=None,
            expiry_date=today + timedelta(days=400)
        ),
        Medicine(
            name="Cetirizine",
            generic_name="Cetirizine Hydrochloride",
            strength="10 mg",
            form="Tablet",
            purpose="Seasonal allergic rhinitis and antihistamine relief",
            instructions="Take at bedtime if drowsiness occurs.",
            frequency="Once Daily",
            reminder_time="22:00",
            quantity=8,
            low_stock_threshold=5,
            start_date=today - timedelta(days=90),
            end_date=None,
            expiry_date=today - timedelta(days=12)  # Expired
        ),
        Medicine(
            name="Paracetamol",
            generic_name="Acetaminophen",
            strength="650 mg",
            form="Tablet",
            purpose="Fever and acute mild-to-moderate pain",
            instructions="Take after light meal with plenty of water. Do not exceed 3g daily.",
            frequency="As Needed",
            reminder_time="14:00",
            quantity=18,
            low_stock_threshold=5,
            start_date=today - timedelta(days=10),
            end_date=None,
            expiry_date=today + timedelta(days=300)
        )
    ]

    for med in sample_medicines:
        # Check if already present to avoid duplication
        existing = Medicine.query.filter_by(name=med.name).first()
        if not existing:
            db.session.add(med)
    db.session.commit()

    # Query persistent medicines
    med_metformin = Medicine.query.filter_by(name="Metformin").first()
    med_lisinopril = Medicine.query.filter_by(name="Lisinopril").first()

    def add_dose_if_missing(med_id, sched_time, l_date, status, taken_time_str=None, note=None):
        exists = DoseLog.query.filter_by(
            medicine_id=med_id,
            scheduled_time=sched_time,
            log_date=l_date
        ).first()
        if not exists:
            t_at = None
            if taken_time_str:
                parsed_time = datetime.strptime(taken_time_str, "%H:%M").time()
                t_at = datetime.combine(l_date, parsed_time, tzinfo=timezone.utc)
            db.session.add(DoseLog(
                medicine_id=med_id,
                scheduled_time=sched_time,
                log_date=l_date,
                status=status,
                taken_at=t_at,
                notes=note
            ))

    if med_metformin and med_lisinopril:
        for offset in range(6, 0, -1):
            log_day = today - timedelta(days=offset)
            # Metformin morning dose
            add_dose_if_missing(med_metformin.id, "08:00", log_day, "Taken", "08:15")
            
            # Metformin evening dose (missed on day -3)
            if offset != 3:
                add_dose_if_missing(med_metformin.id, "20:00", log_day, "Taken", "20:10")
            else:
                add_dose_if_missing(med_metformin.id, "20:00", log_day, "Missed", note="Away from home")

            # Lisinopril morning dose (missed on day -5)
            if offset != 5:
                add_dose_if_missing(med_lisinopril.id, "08:00", log_day, "Taken", "08:05")
            else:
                add_dose_if_missing(med_lisinopril.id, "08:00", log_day, "Missed", note="Fasting for lab test")

        # Today: log morning dose for Lisinopril as taken
        add_dose_if_missing(med_lisinopril.id, "08:00", today, "Taken", "08:10")

        db.session.commit()
