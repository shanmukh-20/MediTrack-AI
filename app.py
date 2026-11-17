"""
app.py
MediTrack AI - Smart Medicine & Health Management System
Main Flask application entry point with full routing and integration.
"""

import os
from datetime import date, datetime, timedelta
from collections import defaultdict
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, abort
)
from models import db, Medicine, DoseLog
from database import init_db, seed_demonstration_data
from safety_data import check_drug_interactions, get_available_knowledge_drugs


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'meditrack-ai-college-project-2026-key'

    # SQLite DB path inside project root
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'meditrack.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize DB and seed sample data if empty
    init_db(app)

    # ------------------------------------------------------------------
    # Context Processor – values available in every template
    # ------------------------------------------------------------------
    @app.context_processor
    def inject_globals():
        return {
            'today': date.today(),
            'current_date': date.today(),
            'current_year': date.today().year,
            'app_name': 'MediTrack AI',
            'app_subtitle': 'Smart Medicine & Health Management System'
        }

    # ------------------------------------------------------------------
    # Helper: Build today's dose schedule
    # ------------------------------------------------------------------
    def _build_today_schedule():
        today = date.today()
        medicines = Medicine.query.all()

        today_logs = DoseLog.query.filter_by(log_date=today).all()
        logged_map = {(lg.medicine_id, lg.scheduled_time): lg for lg in today_logs}

        entries = []
        for med in medicines:
            if med.is_expired:
                continue
            if med.end_date and med.end_date < today:
                continue
            if med.start_date > today:
                continue

            for t in med.get_scheduled_times_list():
                log = logged_map.get((med.id, t))
                is_taken  = log is not None and log.status == 'Taken'
                is_missed = log is not None and log.status == 'Missed'
                status_str = 'Taken' if is_taken else ('Missed' if is_missed else 'Pending')
                entries.append({
                    'medicine':       med,
                    'medicine_id':    med.id,
                    'medicine_name':  med.name,
                    'generic_name':   med.generic_name or '',
                    'strength':       med.strength,
                    'form':           med.form,
                    'frequency':      med.frequency,
                    'instructions':   med.instructions or 'Take as directed.',
                    'scheduled_time': t,
                    'time':           t,
                    'status':         status_str,
                    'is_taken':       is_taken,
                    'log_entry':      log,
                    'log_id':         log.id if log else None,
                })

        entries.sort(key=lambda x: x['scheduled_time'])
        return entries

    # ------------------------------------------------------------------
    # Route 1: Dashboard
    # ------------------------------------------------------------------
    @app.route('/')
    def dashboard():
        medicines = Medicine.query.all()

        total_medicines     = len(medicines)
        active_count        = sum(1 for m in medicines if m.status_label == 'Active')
        low_stock_count     = sum(1 for m in medicines if m.is_low_stock or m.quantity <= 0)
        expiring_soon_count = sum(1 for m in medicines if m.is_expiring_soon)

        today_schedule      = _build_today_schedule()
        today_doses_count   = len(today_schedule)
        today_taken_count   = sum(1 for d in today_schedule if d['is_taken'])

        if today_doses_count > 0:
            today_adherence = round((today_taken_count / today_doses_count) * 100)
        else:
            today_adherence = 100 if total_medicines > 0 else 0

        recent_medicines = Medicine.query.order_by(Medicine.created_at.desc()).limit(8).all()

        stats = {
            'total':        total_medicines,
            'active':       active_count,
            'low_stock':    low_stock_count,
            'expiring_soon': expiring_soon_count,
        }

        return render_template(
            'dashboard.html',
            total_medicines=total_medicines,
            expiring_soon_count=expiring_soon_count,
            low_stock_count=low_stock_count,
            today_doses_count=today_doses_count,
            today_taken_count=today_taken_count,
            today_adherence=today_adherence,
            today_schedule=today_schedule,
            schedule=today_schedule,
            recent_medicines=recent_medicines,
            stats=stats,
            low_stock_alerts=[m for m in medicines if m.is_low_stock],
            expiring_alerts=[m for m in medicines if m.is_expiring_soon],
        )

    # ------------------------------------------------------------------
    # Route 2: Medicines List
    # ------------------------------------------------------------------
    @app.route('/medicines')
    def medicines_list():
        query_text    = request.args.get('q', '').strip()
        status_filter = request.args.get('status', 'all').strip().lower()

        base_query = Medicine.query
        if query_text:
            search_pat = f"%{query_text}%"
            base_query = base_query.filter(
                (Medicine.name.ilike(search_pat)) |
                (Medicine.generic_name.ilike(search_pat)) |
                (Medicine.purpose.ilike(search_pat))
            )

        all_medicines = base_query.order_by(Medicine.name.asc()).all()

        filtered_medicines = []
        for m in all_medicines:
            status_label, _, _ = m.get_status_info()
            if status_filter == 'all':
                filtered_medicines.append(m)
            elif status_filter == 'active' and status_label == 'Active':
                filtered_medicines.append(m)
            elif status_filter == 'expiring_soon' and status_label == 'Expiring Soon':
                filtered_medicines.append(m)
            elif status_filter == 'expired' and status_label == 'Expired':
                filtered_medicines.append(m)
            elif status_filter == 'low_stock' and (status_label in ('Low Stock', 'Out of Stock') or m.is_low_stock):
                filtered_medicines.append(m)

        return render_template(
            'medicines.html',
            medicines=filtered_medicines,
            total_count=len(filtered_medicines),
            query_text=query_text,
            status_filter=status_filter
        )

    # ------------------------------------------------------------------
    # Route 3: Add Medicine (Endpoints: medicine_add, add_medicine)
    # ------------------------------------------------------------------
    @app.route('/medicines/add', methods=['GET', 'POST'], endpoint='medicine_add')
    @app.route('/medicines/new', methods=['GET', 'POST'], endpoint='add_medicine')
    def medicine_add():
        if request.method == 'POST':
            name           = request.form.get('name', '').strip()
            generic_name   = request.form.get('generic_name', '').strip()
            strength       = request.form.get('strength', '').strip()
            form_type      = request.form.get('form', '').strip()
            purpose        = request.form.get('purpose', '').strip()
            instructions   = request.form.get('instructions', '').strip()
            frequency      = request.form.get('frequency', '').strip()
            reminder_times = request.form.getlist('reminder_time')
            if reminder_times and any(t.strip() for t in reminder_times):
                reminder_time = ', '.join(t.strip() for t in reminder_times if t.strip())
            else:
                reminder_time = request.form.get('reminder_time', '').strip()
            quantity_val   = request.form.get('quantity', '10').strip()
            low_stock_val  = request.form.get('low_stock_threshold', '5').strip()
            start_date_str = request.form.get('start_date', '').strip()
            end_date_str   = request.form.get('end_date', '').strip()
            expiry_date_str= request.form.get('expiry_date', '').strip()

            if not name or not strength or not form_type or not frequency or not reminder_time or not expiry_date_str:
                flash('Please complete all required fields.', 'danger')
                return render_template('medicine_form.html', action='Add', form_data=request.form)

            try:
                quantity = max(0, int(quantity_val))
                low_stock_threshold = max(1, int(low_stock_val))
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else date.today()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
            except ValueError:
                flash('Invalid date or number format entered. Please verify your inputs.', 'danger')
                return render_template('medicine_form.html', action='Add', form_data=request.form)

            new_med = Medicine(
                name=name,
                generic_name=generic_name,
                strength=strength,
                form=form_type,
                purpose=purpose,
                instructions=instructions,
                frequency=frequency,
                reminder_time=reminder_time,
                quantity=quantity,
                low_stock_threshold=low_stock_threshold,
                start_date=start_date,
                end_date=end_date,
                expiry_date=expiry_date
            )
            db.session.add(new_med)
            db.session.commit()
            flash(f'Medicine "{name}" has been successfully added to your inventory.', 'success')
            return redirect(url_for('medicines_list'))

        return render_template('medicine_form.html', action='Add', form_data={
            'quantity': 10,
            'low_stock_threshold': 5,
            'start_date': date.today().strftime('%Y-%m-%d'),
            'frequency': 'Once Daily',
            'form': 'Tablet'
        })

    # ------------------------------------------------------------------
    # Route 4: Edit Medicine (Endpoints: medicine_edit, edit_medicine)
    # ------------------------------------------------------------------
    @app.route('/medicines/<int:med_id>/edit', methods=['GET', 'POST'], endpoint='medicine_edit')
    @app.route('/medicines/edit/<int:id>', methods=['GET', 'POST'], endpoint='edit_medicine')
    def medicine_edit(med_id=None, id=None):
        actual_id = med_id if med_id is not None else id
        med = Medicine.query.get_or_404(actual_id)

        if request.method == 'POST':
            med.name         = request.form.get('name', '').strip()
            med.generic_name = request.form.get('generic_name', '').strip()
            med.strength     = request.form.get('strength', '').strip()
            med.form         = request.form.get('form', '').strip()
            med.purpose      = request.form.get('purpose', '').strip()
            med.instructions = request.form.get('instructions', '').strip()
            med.frequency    = request.form.get('frequency', '').strip()
            
            reminder_times = request.form.getlist('reminder_time')
            if reminder_times and any(t.strip() for t in reminder_times):
                med.reminder_time = ', '.join(t.strip() for t in reminder_times if t.strip())
            else:
                raw_time = request.form.get('reminder_time', '').strip()
                if raw_time:
                    med.reminder_time = raw_time

            quantity_val    = request.form.get('quantity', '0').strip()
            low_stock_val   = request.form.get('low_stock_threshold', '5').strip()
            start_date_str  = request.form.get('start_date', '').strip()
            end_date_str    = request.form.get('end_date', '').strip()
            expiry_date_str = request.form.get('expiry_date', '').strip()

            if not med.name or not med.strength or not med.form:
                flash('Please fill in the required fields.', 'danger')
                return render_template('medicine_form.html', action='Edit', medicine=med)

            try:
                med.quantity = max(0, int(quantity_val))
                med.low_stock_threshold = max(1, int(low_stock_val))
                if expiry_date_str:
                    med.expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                if start_date_str:
                    med.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                med.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
            except ValueError:
                flash('Invalid date or number format entered.', 'danger')
                return render_template('medicine_form.html', action='Edit', medicine=med)

            db.session.commit()
            flash(f'Medicine "{med.name}" was successfully updated.', 'success')
            return redirect(url_for('medicine_detail', med_id=med.id))

        return render_template('medicine_form.html', action='Edit', medicine=med)

    # ------------------------------------------------------------------
    # Route 5: Medicine Detail (Endpoints: medicine_detail, supports med_id & id)
    # ------------------------------------------------------------------
    @app.route('/medicines/<int:med_id>', endpoint='medicine_detail')
    @app.route('/medicines/detail/<int:id>', endpoint='medicine_detail_id')
    def medicine_detail(med_id=None, id=None):
        actual_id = med_id if med_id is not None else id
        med = Medicine.query.get_or_404(actual_id)
        dose_history = (
            DoseLog.query
            .filter_by(medicine_id=med.id)
            .order_by(DoseLog.log_date.desc(), DoseLog.taken_at.desc())
            .limit(30).all()
        )
        days_to_expiry = (med.expiry_date - date.today()).days
        return render_template(
            'medicine_detail.html',
            medicine=med,
            dose_history=dose_history,
            logs=dose_history,
            days_to_expiry=days_to_expiry,
            days_until_expiry=days_to_expiry
        )

    # ------------------------------------------------------------------
    # Route 6: Delete Medicine (Endpoints: medicine_delete, delete_medicine)
    # ------------------------------------------------------------------
    @app.route('/medicines/<int:med_id>/delete', methods=['POST'], endpoint='medicine_delete')
    @app.route('/medicines/delete/<int:id>', methods=['POST'], endpoint='delete_medicine')
    def medicine_delete(med_id=None, id=None):
        actual_id = med_id if med_id is not None else id
        med = Medicine.query.get_or_404(actual_id)
        name = med.name
        db.session.delete(med)
        db.session.commit()
        flash(f'Medicine "{name}" and its associated logs have been removed.', 'info')
        return redirect(url_for('medicines_list'))

    # ------------------------------------------------------------------
    # Route 7: Reminders
    # ------------------------------------------------------------------
    @app.route('/reminders')
    def reminders():
        today_schedule = _build_today_schedule()
        filter_status  = request.args.get('status', 'all')

        if filter_status == 'pending':
            filtered_schedule = [s for s in today_schedule if not s['is_taken']]
        elif filter_status == 'taken':
            filtered_schedule = [s for s in today_schedule if s['is_taken']]
        else:
            filtered_schedule = today_schedule

        total = len(today_schedule)
        taken = sum(1 for s in today_schedule if s['is_taken'])
        pending = total - taken
        adherence_rate = round((taken / total) * 100) if total > 0 else 100

        return render_template(
            'reminders.html',
            schedule=filtered_schedule,
            total_count=total,
            taken_count=taken,
            pending_count=pending,
            filter_status=filter_status,
            adherence_rate=adherence_rate
        )

    # ------------------------------------------------------------------
    # Route 8: Mark Dose as Taken / Missed
    # ------------------------------------------------------------------
    @app.route('/reminders/mark-taken', methods=['POST'], endpoint='mark_dose_taken')
    @app.route('/reminders/mark', methods=['POST'], endpoint='mark_dose')
    def mark_dose_taken():
        # Handle JSON or Form
        data = request.get_json(silent=True) or request.form
        med_id_val     = data.get('medicine_id')
        scheduled_time = (data.get('scheduled_time') or '').strip()
        redirect_target= data.get('next', 'reminders')
        status_input   = (data.get('status') or 'Taken').strip().title()
        status         = 'Taken' if status_input.lower() in ('taken', 'true', '1') else 'Missed'

        if not med_id_val or not scheduled_time:
            if request.is_json:
                return jsonify(success=False, error='Invalid parameters'), 400
            flash('Invalid dose parameters received.', 'danger')
            return redirect(url_for('reminders'))

        try:
            med_id = int(med_id_val)
        except (ValueError, TypeError):
            if request.is_json:
                return jsonify(success=False, error='Invalid medicine id'), 400
            flash('Invalid medicine identifier.', 'danger')
            return redirect(url_for('reminders'))

        med = Medicine.query.get_or_404(med_id)
        today = date.today()

        existing_log = DoseLog.query.filter_by(
            medicine_id=med.id,
            log_date=today,
            scheduled_time=scheduled_time
        ).first()

        if existing_log:
            existing_log.status = status
            existing_log.taken_at = datetime.now()
        else:
            new_log = DoseLog(
                medicine_id=med.id,
                scheduled_time=scheduled_time,
                log_date=today,
                status=status,
                taken_at=datetime.now()
            )
            db.session.add(new_log)
            if status == 'Taken' and med.quantity > 0:
                med.quantity -= 1

        db.session.commit()

        # Adherence calculation for JSON response
        flat = _build_today_schedule()
        tot = len(flat)
        tk = sum(1 for e in flat if e['is_taken'])
        adh = round((tk / tot) * 100) if tot > 0 else 100

        if request.is_json:
            return jsonify(success=True, status=status.lower(), adherence_rate=adh)

        flash(f'Marked dose as {status} for {med.name} ({scheduled_time}).', 'success')
        if redirect_target == 'dashboard':
            return redirect(url_for('dashboard'))
        return redirect(url_for('reminders'))

    # ------------------------------------------------------------------
    # Route 9: Safety Checker (Endpoints: safety_checker, safety, safety_check)
    # ------------------------------------------------------------------
    @app.route('/safety', methods=['GET', 'POST'], endpoint='safety_checker')
    @app.route('/safety/check', methods=['GET', 'POST'], endpoint='safety_check')
    @app.route('/safety/view', methods=['GET', 'POST'], endpoint='safety')
    def safety_checker():
        user_medicines  = Medicine.query.order_by(Medicine.name.asc()).all()
        knowledge_drugs = get_available_knowledge_drugs()

        check_results      = None
        result             = None
        selected_medicines = []
        drug1              = ''
        drug2              = ''

        # Handle JSON API request (e.g. from app.js)
        json_data = request.get_json(silent=True)
        if json_data:
            drug1 = json_data.get('drug1', '').strip()
            drug2 = json_data.get('drug2', '').strip()
            if not drug1 or not drug2:
                return jsonify(interaction=False, message='Please enter both drug names to check.')
            check = check_drug_interactions([drug1, drug2])
            if check['interaction_count'] > 0:
                r = check['results'][0]
                severity_map = {'Severe': 'high', 'Moderate': 'medium', 'Mild': 'low'}
                return jsonify({
                    'interaction': True,
                    'severity': severity_map.get(r['severity'], 'medium'),
                    'message': f"{r['title']}: {r['mechanism']} Practical Guidance: {r['management']}"
                })
            return jsonify({
                'interaction': False,
                'message': f"No documented clinical interaction found between {drug1} and {drug2} in the demonstration database."
            })

        # Handle HTML Form POST
        if request.method == 'POST':
            form_meds    = request.form.getlist('medicines')
            custom_input = request.form.get('custom_medicines', '').strip()
            d1           = request.form.get('drug1', '').strip()
            d2           = request.form.get('drug2', '').strip()

            combined = []
            if form_meds:
                combined.extend(form_meds)
            if custom_input:
                raw_items = custom_input.replace(';', ',').replace('\n', ',').split(',')
                combined.extend([item.strip() for item in raw_items if item.strip()])
            if d1 and d2:
                combined.extend([d1, d2])
                drug1 = d1
                drug2 = d2

            seen_clean = set()
            for item in combined:
                if item.lower() not in seen_clean:
                    seen_clean.add(item.lower())
                    selected_medicines.append(item)

            if len(selected_medicines) < 2:
                flash('Please select or enter at least two medicines to check for potential drug interactions.', 'warning')
            else:
                check_results = check_drug_interactions(selected_medicines)
                if check_results['interaction_count'] > 0:
                    r = check_results['results'][0]
                    result = {
                        'has_interaction': True,
                        'title': r['title'],
                        'severity': r['severity'],
                        'description': r['mechanism'],
                        'management': r['management']
                    }
                else:
                    result = {'has_interaction': False}

        return render_template(
            'safety.html',
            user_medicines=user_medicines,
            medicines=user_medicines,
            knowledge_drugs=knowledge_drugs,
            selected_medicines=selected_medicines,
            check_results=check_results,
            result=result,
            drug1=drug1,
            drug2=drug2
        )

    # ------------------------------------------------------------------
    # Route 10: Analytics Page
    # ------------------------------------------------------------------
    @app.route('/analytics')
    def analytics():
        today    = date.today()
        all_logs = DoseLog.query.all()
        medicines= Medicine.query.all()

        total_logged = len(all_logs)
        taken_count  = sum(1 for l in all_logs if l.status == 'Taken')
        missed_count = sum(1 for l in all_logs if l.status == 'Missed')

        if total_logged > 0:
            adherence_rate = round((taken_count / total_logged) * 100, 1)
        else:
            adherence_rate = 0.0

        # Bar chart data: Doses taken by medicine
        med_counts = {}
        for l in all_logs:
            if l.status == 'Taken':
                name = l.medicine.name if l.medicine else f"Med #{l.medicine_id}"
                med_counts[name] = med_counts.get(name, 0) + 1

        med_labels = list(med_counts.keys())
        med_values = [med_counts[k] for k in med_labels]

        # Line chart data: Daily activity (Last 7 Days)
        days_labels = []
        daily_taken_values = []
        for i in range(6, -1, -1):
            target_date = today - timedelta(days=i)
            day_str = target_date.strftime('%b %d')
            days_labels.append(day_str)
            count = sum(1 for l in all_logs if l.log_date == target_date and l.status == 'Taken')
            daily_taken_values.append(count)

        chart_data = {
            'adherence': {
                'taken': taken_count,
                'missed': missed_count
            },
            'medicine_doses': {
                'labels': med_labels,
                'values': med_values
            },
            'daily_activity': {
                'labels': days_labels,
                'values': daily_taken_values
            }
        }

        return render_template(
            'analytics.html',
            total_logged=total_logged,
            taken_count=taken_count,
            missed_count=missed_count,
            adherence_rate=adherence_rate,
            has_data=total_logged > 0,
            chart_data=chart_data
        )

    # ------------------------------------------------------------------
    # Route 11: Analytics Data (JSON)
    # ------------------------------------------------------------------
    @app.route('/analytics/data')
    def analytics_data():
        today    = date.today()
        all_logs = DoseLog.query.all()
        meds     = Medicine.query.all()

        taken_by_day  = defaultdict(int)
        missed_by_day = defaultdict(int)
        for lg in all_logs:
            key = lg.log_date.strftime('%b %d')
            if lg.status == 'Taken':
                taken_by_day[key]  += 1
            elif lg.status == 'Missed':
                missed_by_day[key] += 1

        day_labels = []
        taken_vals = []
        missed_vals = []
        for i in range(29, -1, -1):
            d   = today - timedelta(days=i)
            lbl = d.strftime('%b %d')
            day_labels.append(lbl)
            taken_vals.append(taken_by_day.get(lbl, 0))
            missed_vals.append(missed_by_day.get(lbl, 0))

        form_counts = defaultdict(int)
        for m in meds:
            form_counts[m.form] += 1
        form_labels = list(form_counts.keys())
        form_counts_list = [form_counts[k] for k in form_labels]

        med_adh_labels = []
        med_adh_rates  = []
        for m in meds:
            logs_for_m = [lg for lg in all_logs if lg.medicine_id == m.id]
            total_m = len(logs_for_m)
            taken_m = sum(1 for lg in logs_for_m if lg.status == 'Taken')
            rate    = round((taken_m / total_m * 100)) if total_m > 0 else 0
            med_adh_labels.append(m.name)
            med_adh_rates.append(rate)

        total_taken  = sum(1 for lg in all_logs if lg.status == 'Taken')
        total_missed = sum(1 for lg in all_logs if lg.status == 'Missed')

        return jsonify({
            'doses_per_day': {
                'labels': day_labels,
                'taken':  taken_vals,
                'missed': missed_vals,
            },
            'medicine_by_form': {
                'labels': form_labels,
                'counts': form_counts_list,
            },
            'adherence_rate': {
                'labels': med_adh_labels,
                'rates':  med_adh_rates,
            },
            'taken_vs_missed': {
                'taken':  total_taken,
                'missed': total_missed,
            },
        })

    # ------------------------------------------------------------------
    # Route 12: Biology Education
    # ------------------------------------------------------------------
    @app.route('/biology')
    def biology():
        return render_template('biology.html')

    # ------------------------------------------------------------------
    # Route 13: About Page
    # ------------------------------------------------------------------
    @app.route('/about')
    def about():
        return render_template('about.html')

    # ------------------------------------------------------------------
    # Route 14: Seed Demo Data
    # ------------------------------------------------------------------
    @app.route('/seed-demo', methods=['POST'])
    def seed_demo():
        DoseLog.query.delete()
        Medicine.query.delete()
        db.session.commit()
        seed_demonstration_data()
        flash('Sample demonstration dataset loaded successfully with balanced sample medicines and adherence history.', 'success')
        return redirect(url_for('dashboard'))

    # ------------------------------------------------------------------
    # API Endpoints
    # ------------------------------------------------------------------
    @app.route('/api/medicines')
    def api_medicines():
        q = request.args.get('q', '').strip()
        query = Medicine.query
        if q:
            query = query.filter(Medicine.name.ilike(f'%{q}%'))
        meds = query.order_by(Medicine.name).all()
        return jsonify([{
            'id': m.id,
            'name': m.name,
            'generic_name': m.generic_name or '',
            'strength': m.strength,
            'form': m.form,
            'quantity': m.quantity,
            'status': m.status_label,
        } for m in meds])

    @app.route('/api/dashboard-stats')
    def api_dashboard_stats():
        medicines = Medicine.query.all()
        flat_schedule = _build_today_schedule()
        today_taken = sum(1 for e in flat_schedule if e['is_taken'])
        today_total = len(flat_schedule)

        return jsonify({
            'total': len(medicines),
            'active': sum(1 for m in medicines if m.status_label == 'Active'),
            'low_stock': sum(1 for m in medicines if m.is_low_stock or m.quantity <= 0),
            'expiring_soon': sum(1 for m in medicines if m.is_expiring_soon),
            'today_total': today_total,
            'today_taken': today_taken,
            'adherence_rate': round((today_taken / today_total * 100)) if today_total > 0 else 100
        })

    @app.route('/api/medicines/<int:med_id>/log-dose', methods=['POST'])
    @app.route('/api/medicines/log/<int:id>', methods=['POST'])
    def api_log_dose(med_id=None, id=None):
        actual_id = med_id if med_id is not None else id
        med = Medicine.query.get_or_404(actual_id)
        data = request.get_json(silent=True) or request.form
        scheduled_time = data.get('scheduled_time', datetime.now().strftime('%H:%M'))
        status = data.get('status', 'Taken').title()

        new_log = DoseLog(
            medicine_id=med.id,
            scheduled_time=scheduled_time,
            log_date=date.today(),
            status=status,
            taken_at=datetime.now()
        )
        db.session.add(new_log)
        if status == 'Taken' and med.quantity > 0:
            med.quantity -= 1
        db.session.commit()

        return jsonify(success=True, medicine=med.name, quantity=med.quantity)

    # ------------------------------------------------------------------
    # Error Handlers
    # ------------------------------------------------------------------
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('404.html', error_title="Server Error", error_message="An unexpected server error occurred. Please navigate back to the dashboard."), 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
