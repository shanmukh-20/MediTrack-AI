from datetime import datetime, date, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_utc_now():
    return datetime.now(timezone.utc)

class Medicine(db.Model):
    __tablename__ = 'medicines'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    generic_name = db.Column(db.String(100), nullable=True)
    strength = db.Column(db.String(50), nullable=False)        # e.g., "500 mg", "10 ml"
    form = db.Column(db.String(50), nullable=False)            # e.g., "Tablet", "Capsule", "Syrup"
    purpose = db.Column(db.String(150), nullable=True)         # e.g., "Hypertension", "Pain Relief"
    instructions = db.Column(db.String(200), nullable=True)    # e.g., "Take after food with water"
    frequency = db.Column(db.String(50), nullable=False)       # e.g., "Once Daily", "Twice Daily"
    reminder_time = db.Column(db.String(50), nullable=False)   # e.g., "08:00" or "08:00, 20:00"
    quantity = db.Column(db.Integer, nullable=False, default=10) # Current count/units
    low_stock_threshold = db.Column(db.Integer, default=5)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    dose_logs = db.relationship('DoseLog', backref='medicine', cascade='all, delete-orphan', lazy=True)

    def get_status_info(self, ref_date=None):
        """
        Determines current medicine status based on real database values and dates.
        Returns a tuple: (status_label, css_badge_class, priority_order)
        """
        if ref_date is None:
            ref_date = date.today()

        days_to_expiry = (self.expiry_date - ref_date).days

        if days_to_expiry < 0:
            return ("Expired", "badge-danger", 1)
        
        if self.quantity <= 0:
            return ("Out of Stock", "badge-danger", 2)

        if days_to_expiry <= 30:
            return ("Expiring Soon", "badge-warning", 3)

        if self.quantity <= self.low_stock_threshold:
            return ("Low Stock", "badge-amber", 4)

        if self.end_date and self.end_date < ref_date:
            return ("Completed", "badge-secondary", 5)

        return ("Active", "badge-success", 6)

    @property
    def status_label(self):
        return self.get_status_info()[0]

    @property
    def status_badge_class(self):
        return self.get_status_info()[1]

    @property
    def is_low_stock(self):
        return 0 < self.quantity <= self.low_stock_threshold

    @property
    def is_expiring_soon(self):
        days = (self.expiry_date - date.today()).days
        return 0 <= days <= 30

    @property
    def is_expired(self):
        return self.expiry_date < date.today()

    def get_scheduled_times_list(self):
        """Returns clean list of reminder times e.g. ['08:00', '20:00']"""
        if not self.reminder_time:
            return []
        times = [t.strip() for t in self.reminder_time.replace(';', ',').split(',') if t.strip()]
        return times


class DoseLog(db.Model):
    __tablename__ = 'dose_logs'

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False)
    scheduled_time = db.Column(db.String(20), nullable=False) # e.g. "08:00"
    log_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default="Taken") # "Taken", "Missed"
    taken_at = db.Column(db.DateTime, default=get_utc_now)
    notes = db.Column(db.String(200), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('medicine_id', 'log_date', 'scheduled_time', name='unique_dose_per_slot'),
    )
