# MediTrack AI – Smart Medicine & Health Management System

A complete, professional web application built with **Python Flask**, **SQLite**, **HTML5**, **CSS3**, **Vanilla JavaScript**, and **Chart.js** designed for personal medicine management, prescription tracking, dosage reminders, adherence analytics, clinical safety checking, and pharmacology education (ADME, Pharmacokinetics, and Pharmacodynamics).

---

## 🌟 Features Overview

### 1. 📊 Executive Dashboard
- **Real-Time KPIs**: Total registered medications, active regimens, low-stock warnings, expiring soon alerts (<30 days), and today's adherence rate.
- **Today's Dose Schedule**: Dynamic timetable showing morning/afternoon/evening doses with 1-click **"Mark as Taken"** action.
- **Inventory Overview**: Quick status indicators with badges for Active, Low Stock, Expiring Soon, Expired, and Completed courses.

### 2. 💊 Medicine Inventory Management (Full CRUD)
- **Comprehensive Profiles**: Brand name, generic/active molecule, strength (e.g., 500 mg), dosage form (Tablet, Capsule, Syrup, Drops, Inhaler, Injection, Ointment), medical purpose, special instructions, frequency, and custom reminder times.
- **Stock Tracking & Alerts**: Dynamic decrementing of inventory quantity when doses are marked as taken, with configurable low-stock thresholds.
- **Expiry Tracking**: Real-time expiration calculation with countdown badges and warning indicators.
- **Live Search & Status Filtering**: Instant search across brand names, generic names, and indications, combined with filter tabs (All, Active, Expiring Soon, Expired, Low Stock).

### 3. ⏰ Reminders & Dose Tracking
- **Daily Intake Schedule**: Doses scheduled for the current date with time slot markers and dosage instructions.
- **Adherence Logging**: One-click dose recording with automatic stock deduction and timestamp logging.
- **Filtering**: View all, pending, or completed doses for the day.

### 4. 🛡️ Drug Safety & Interaction Checker
- **Offline Clinical Knowledge Base**: Comprehensive interaction rules covering 15+ high-risk clinical drug pairs (anticoagulants, statins, ACE inhibitors, NSAIDs, SSRIs, etc.).
- **Biological Mechanism Analysis**: Detailed scientific explanations (e.g., CYP3A4 inhibition, competitive COX-1 binding, P-glycoprotein efflux inhibition, hyperkalemia risks).
- **Practical Guidance**: Evidence-based clinical recommendations and timing adjustments (e.g., spacing calcium and levothyroxine administration by 4 hours).
- **Dual Mode**: Interactive checkbox selector from your registered inventory or manual comma-separated text entry with one-click test combinations.

### 5. 📈 Analytics & Compliance Visualizations
- **Interactive Chart.js Visualizations**:
  - **Adherence Rate Distribution**: Doughnut chart comparing completed vs. missed doses.
  - **Doses Taken by Medicine**: Horizontal bar chart comparing intake frequency across medications.
  - **Daily Activity (Last 7 Days)**: Line chart tracking daily dosage trends over the past week.
- **RESTful Analytics API**: `/analytics/data` endpoint serving structured JSON metrics for external integration.

### 6. 🧬 Biology Education (ADME, PK & PD)
- **ADME Pathway**: Detailed breakdown of **A**bsorption (bioavailability, gastrointestinal transit), **D**istribution (plasma protein binding, volume of distribution), **M**etabolism (Phase I Cytochrome P450 enzymes and Phase II conjugation), and **E**xcretion (renal clearance and biliary elimination).
- **Pharmacokinetics (PK)**: Mathematical definitions and clinical interpretations of Half-life ($t_{1/2}$), $C_{max}$, $T_{max}$, Area Under the Curve (AUC), Clearance ($CL$), and Steady-State Concentration ($C_{ss}$).
- **Pharmacodynamics (PD)**: Agonists, antagonists, competitive inhibition, dose-response relationships, and Therapeutic Index ($TI = TD_{50} / ED_{50}$).
- **Receptor Biology**: G-Protein Coupled Receptors (GPCRs), ligand-gated ion channels, receptor tyrosine kinases, and intracellular nuclear receptors.

### 7. ℹ️ About & Technical Reference
- Project architecture breakdown, problem & solution analysis, data security measures, and regulatory/medical disclaimers.

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.10+ with Flask 3.0+
- **ORM / Database**: Flask-SQLAlchemy 3.1+ with SQLite 3 (ACID compliant)
- **Frontend**: Clean Semantic HTML5, Modular CSS3 Design System with CSS variables (no AI gradients), Vanilla ES6+ JavaScript
- **Data Visualization**: Chart.js 4.4+
- **Testing**: Python `unittest` framework with in-memory SQLite isolation

---

## 📁 Project Directory Structure

```text
MediTrack-AI/
├── app.py                  # Core Flask application, routing, and REST API endpoints
├── models.py               # SQLAlchemy models (Medicine and DoseLog)
├── database.py             # Database initialization and sample clinical seed data
├── safety_data.py          # Pharmacology interaction knowledge base and rules
├── test_app.py             # Automated unit test suite (17 comprehensive test cases)
├── requirements.txt        # Python dependency manifest
├── README.md               # Project documentation
├── static/
│   ├── css/
│   │   └── style.css       # Clean healthcare design system (responsive layout)
│   └── js/
│       ├── main.js         # Core UI interactions and alerts
│       ├── charts.js       # Chart.js initialization logic
│       └── app.js          # Client-side utility functions and helpers
└── templates/
    ├── base.html           # Master layout with navigation and flash messages
    ├── dashboard.html      # Overview dashboard with KPIs and today's schedule
    ├── medicines.html      # Medication inventory list with live search and filters
    ├── medicine_form.html  # Unified Add / Edit medication form
    ├── medicine_detail.html# Full medicine profile and 30-day dose history
    ├── reminders.html      # Daily dose schedule and intake recording
    ├── safety.html         # Drug interaction checker with biological mechanisms
    ├── analytics.html      # Adherence graphs and statistics
    ├── biology.html        # Comprehensive pharmacology guide (ADME, PK, PD)
    ├── about.html          # Project overview, architecture, and disclaimers
    └── 404.html            # User-friendly error page
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10 or later installed on your system.

### 2. Installation
Clone or navigate to the repository folder:
```powershell
cd c:\Users\telug\Downloads\MediTrack-AI
```

Install the dependencies:
```powershell
pip install -r requirements.txt
```

### 3. Running the Application
Start the Flask development server:
```powershell
python app.py
```
Open your web browser and navigate to:
```text
http://127.0.0.1:5000/
```

*Note: On the first run, the SQLite database (`meditrack.db`) is automatically initialized and seeded with representative demonstration medicines (Metformin, Atorvastatin, Amoxicillin, Lisinopril, Cetirizine, Paracetamol) and past dosage logs.*

---

## 🧪 Running Automated Tests

To execute the unit test suite verifying all routes, CRUD operations, APIs, and safety logic:
```powershell
python -m unittest test_app.py
```

All 17 test cases run against an isolated in-memory SQLite database (`sqlite:///:memory:`).

---

## 🌐 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/medicines` | `GET` | Returns list of registered medicines in JSON. Supports `?q=` search query. |
| `GET /api/dashboard-stats` | `GET` | Returns real-time KPI metrics for dashboard cards. |
| `POST /api/medicines/<id>/log-dose` | `POST` | Logs a dose event for a specific medicine. Decrements stock on `Taken`. |
| `POST /reminders/mark` | `POST` | Records a dose intake as `Taken` or `Missed`. Returns updated adherence rate. |
| `POST /safety/check` | `POST` | Evaluates pairwise drug interaction between two medication strings via JSON. |
| `GET /analytics/data` | `GET` | Returns adherence datasets, form breakdowns, and daily activity metrics. |

---

## ⚠️ Medical Disclaimer
This software is an educational prototype and computer science project. It is **not** a certified medical device and does not constitute medical advice, diagnosis, or clinical prescription. Users should always consult qualified healthcare professionals regarding medication regimens.
