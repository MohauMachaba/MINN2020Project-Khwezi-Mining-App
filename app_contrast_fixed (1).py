import os
import pandas as pd
import streamlit as st

# =========================
# App configuration
# =========================
st.set_page_config(
    page_title="SafeMine360 - Khwezi Mining",
    page_icon="⚒️",
    layout="wide",
)

WORKERS_FILE = "workers.csv"
INCIDENTS_FILE = "safety_incidents.csv"
EQUIPMENT_FILE = "equipment.csv"
MAINTENANCE_FILE = "maintenance.csv"
RISK_FILE = "risk_assessments.csv"
ACCOUNTS_FILE = "user_accounts.csv"

# =========================
# Styling
# =========================

def apply_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [data-testid="stAppViewContainer"], .stApp, .stMain {
            background: linear-gradient(180deg, rgba(6, 18, 27, 0.96) 0%, rgba(15, 23, 42, 0.98) 42%, rgba(3, 7, 18, 1) 100%);
            font-family: 'Inter', sans-serif;
            color: #f8fafc !important;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .main > div {
            background: transparent;
        }

        .stSidebar > div {
            background: rgba(15, 23, 42, 0.86);
            border-right: 1px solid rgba(148, 163, 184, 0.25);
        }

        .stSidebar *, .stSidebar p, .stSidebar label, .stSidebar div,
        .stSidebar span, .stSidebar li, .stSidebar a {
            color: #f8fafc !important;
        }

        .hero {
            padding: 2rem 1.5rem;
            border-radius: 22px;
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148,163,184,0.25);
            box-shadow: 0 12px 30px rgba(0,0,0,0.18);
            backdrop-filter: blur(5px);
        }

        .hero h1 {
            font-size: 3rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 0.3rem;
            line-height: 1.1;
        }

        .hero p {
            font-size: 1.08rem;
            color: #e2e8f0;
            margin-bottom: 0;
        }

        .small-label {
            color: #dbeafe;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .glass-card {
            background: rgba(15, 23, 42, 0.68);
            border: 1px solid rgba(148,163,184,0.20);
            border-radius: 18px;
            padding: 1rem 1rem 1.2rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.12);
        }

        .section-title {
            color: #f8fafc;
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }

        /* Global high-contrast text defaults for the dark app background */
        h1, h2, h3, h4, h5, h6, p, div, span, label, li, a, strong, b, em, code,
        small, summary, dt, dd, legend, caption {
            color: #f8fafc;
        }

        /* Keep text readable inside common Streamlit containers and messages */
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] strong,
        [data-testid="stMarkdownContainer"] em,
        [data-testid="stCaptionContainer"],
        [data-testid="stHeader"],
        [data-testid="stSubheader"],
        .stText, .stCaption, .stAlert p, .stAlert span,
        .stExpander, .stExpander summary {
            color: #f8fafc !important;
        }

        /* Tables and dataframe text: dark text on a light surface */
        [data-testid="stDataFrame"],
        [data-testid="stDataEditor"],
        [data-testid="stTable"] {
            color: #0f172a !important;
        }

        /* Inputs: readable dark text on white/light input backgrounds */
        input, textarea,
        [data-baseweb="select"] *,
        [data-baseweb="input"] *,
        [data-baseweb="textarea"] *,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTimeInput"] input {
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a;
        }

        input::placeholder, textarea::placeholder {
            color: #475569 !important;
            -webkit-text-fill-color: #475569;
            opacity: 1;
        }

        /* Dropdown menus and popovers use a light surface */
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        [role="listbox"],
        [role="option"] {
            color: #0f172a !important;
            background-color: #ffffff !important;
        }

        [role="option"] * {
            color: #0f172a !important;
        }

        /* Buttons use a light surface, so their text must remain dark */
        .stButton > button,
        .stFormSubmitButton > button,
        button[kind="primary"],
        button[kind="secondary"] {
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
        }

        /* Make chart labels and axes readable against chart backgrounds */
        [data-testid="stVegaLiteChart"],
        [data-testid="stArrowVegaLiteChart"],
        [data-testid="stPlotlyChart"],
        [data-testid="stAltairChart"] {
            color: #f8fafc !important;
        }

        /* Status messages have tinted backgrounds; use strong readable text */
        .info-box { color: #e0f2fe !important; }
        .success-box { color: #dcfce7 !important; }
        .warning-box { color: #fef3c7 !important; }
        .danger-box { color: #fee2e2 !important; }

        .stMetric > div {
            background: rgba(15, 23, 42, 0.78);
            border: 1px solid rgba(148,163,184,0.20);
            border-radius: 16px;
            padding: 0.7rem 0.9rem;
            box-shadow: 0 10px 18px rgba(0,0,0,0.10);
        }

        .stMetric label {
            color: #e2e8f0 !important;
            font-size: 0.8rem !important;
            font-weight: 600;
        }

        .stMetric [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-size: 1.8rem !important;
            font-weight: 800 !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #f8fafc 0%, #dfe7f5 100%);
            color: #0f172a;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            padding: 0.75rem 1.2rem;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 18px rgba(0,0,0,0.10);
        }

        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div,
        .stNumberInput > div > div > input,
        .stDateInput > div > div,
        .stTimeInput > div > div,
        .stFileUploader > div,
        .stRadio > div,
        .stCheckbox > div {
            background: rgba(255,255,255,0.96) !important;
            color: #0f172a !important;
            border-radius: 10px;
            border: 1px solid rgba(148,163,184,0.60);
        }

        .stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label,
        .stDateInput label, .stTimeInput label, .stFileUploader label, .stCheckbox label, .stRadio label {
            color: #f8fafc !important;
            font-weight: 600;
        }

        .stRadio > div {
            background: rgba(15,23,42,0.72) !important;
            border-radius: 999px;
            padding: 6px 8px;
            border: 1px solid rgba(148,163,184,0.20);
        }

        .stRadio label {
            color: #f8fafc !important;
            font-weight: 600;
        }

        .stCheckbox label, .stCheckbox label span {
            color: #f8fafc !important;
        }

        [data-testid="stSlider"] label,
        [data-testid="stSlider"] p {
            color: #f8fafc !important;
        }

        /* Dataframe headers/cells may use separate Streamlit DOM elements */
        [data-testid="stDataFrame"] *,
        [data-testid="stDataEditor"] * {
            color: #0f172a !important;
        }

        .stDataFrame {
            background: rgba(15, 23, 42, 0.68);
            border: 1px solid rgba(148,163,184,0.15);
            border-radius: 12px;
        }

        .stDataFrame .stDataFrameContainer, .stDataFrameContainer {
            color: #f8fafc !important;
        }

        .info-box {
            background: rgba(14,165,233,0.12);
            border: 1px solid rgba(56,189,248,0.35);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            color: #e0f2fe;
        }

        .success-box {
            background: rgba(34,197,94,0.10);
            border: 1px solid rgba(34,197,94,0.35);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            color: #dcfce7;
        }

        .warning-box {
            background: rgba(251,191,36,0.10);
            border: 1px solid rgba(251,191,36,0.35);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            color: #fef3c7;
        }

        .danger-box {
            background: rgba(239,68,68,0.12);
            border: 1px solid rgba(239,68,68,0.35);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            color: #fee2e2;
        }

        .stAlert {
            border-radius: 12px;
        }

        .stSuccess, .stError, .stWarning, .stInfo {
            color: #f8fafc !important;
        }

        [data-testid="stSidebarNav"] a, [data-testid="stSidebarNav"] span,
        [data-testid="stSidebarNav"] div, [data-testid="stSidebarNav"] li {
            color: #f8fafc !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_custom_css()

# =========================
# Default data
# =========================
def make_default_workers():
    return pd.DataFrame(
        [
            {
                "Name": "Thabo Dlamini",
                "Worker ID": "W-001",
                "Department": "Mining",
                "Training Status": "Completed",
                "Job Role": "Drill Operator",
                "Shift": "Day",
                "PPE Compliance": "Compliant",
                "Fatigue Level": "Low",
                "Safety Observations": "No issues observed",
                "Near Misses": 0,
                "Previous Incidents": 0,
                "Risk Level": "Low",
            },
            {
                "Name": "Aphiwe Nkosi",
                "Worker ID": "W-002",
                "Department": "Engineering",
                "Training Status": "Completed",
                "Job Role": "Technician",
                "Shift": "Night",
                "PPE Compliance": "Compliant",
                "Fatigue Level": "Medium",
                "Safety Observations": "Monitor fatigue tracking",
                "Near Misses": 1,
                "Previous Incidents": 0,
                "Risk Level": "Medium",
            },
            {
                "Name": "Lerato Moloi",
                "Worker ID": "W-003",
                "Department": "Safety",
                "Training Status": "Completed",
                "Job Role": "Safety Auditor",
                "Shift": "Day",
                "PPE Compliance": "Compliant",
                "Fatigue Level": "Low",
                "Safety Observations": "Clear compliance record",
                "Near Misses": 0,
                "Previous Incidents": 0,
                "Risk Level": "Low",
            },
        ]
    )


def make_default_incidents():
    return pd.DataFrame(
        [
            {
                "Incident ID": 1,
                "Date": "2026-08-01",
                "Time": "08:20",
                "Shift": "Day",
                "Location": "Pit A",
                "Department": "Mining",
                "Incident Type": "Unsafe Condition",
                "Severity": "High",
                "Injury Status": "No",
                "Lost-Time Injury": "No",
                "Description": "Loose rock on access route",
                "Cause": "Poor ground control",
                "Corrective Action": "Area barricaded and inspected",
                "Incident Status": "Resolved",
            },
            {
                "Incident ID": 2,
                "Date": "2026-08-04",
                "Time": "21:30",
                "Shift": "Night",
                "Location": "Crusher Plant",
                "Department": "Engineering",
                "Incident Type": "Near Miss",
                "Severity": "Medium",
                "Injury Status": "No",
                "Lost-Time Injury": "No",
                "Description": "Truck nearly collided with excavator",
                "Cause": "Poor visibility",
                "Corrective Action": "Lighting review",
                "Incident Status": "Under Investigation",
            },
        ]
    )


def make_default_equipment():
    return pd.DataFrame(
        [
            {
                "Equipment Name": "Haul Truck 1",
                "Equipment ID": "EQ-101",
                "Equipment Type": "Truck",
                "Manufacturer": "CAT",
                "Operating Hours": 3500,
                "Temperature": 75,
                "Vibration": 4.2,
                "Fuel Level": 68,
                "Brakes": "Good",
                "Tyres": "Good",
                "Engine": "Good",
                "Downtime": 2.5,
                "Maintenance Status": "Up to date",
            },
            {
                "Equipment Name": "Excavator 2",
                "Equipment ID": "EQ-205",
                "Equipment Type": "Excavator",
                "Manufacturer": "Hitachi",
                "Operating Hours": 4800,
                "Temperature": 96,
                "Vibration": 7.1,
                "Fuel Level": 55,
                "Brakes": "Good",
                "Tyres": "Needs Repair",
                "Engine": "Good",
                "Downtime": 8.0,
                "Maintenance Status": "Due",
            },
            {
                "Equipment Name": "Drill Rig 3",
                "Equipment ID": "EQ-309",
                "Equipment Type": "Drill",
                "Manufacturer": "Atlas Copco",
                "Operating Hours": 2900,
                "Temperature": 82,
                "Vibration": 5.8,
                "Fuel Level": 72,
                "Brakes": "Good",
                "Tyres": "Good",
                "Engine": "Needs Repair",
                "Downtime": 5.0,
                "Maintenance Status": "Overdue",
            },
        ]
    )


def make_default_maintenance():
    return pd.DataFrame(
        [
            {
                "Equipment Name": "Haul Truck 1",
                "Equipment ID": "EQ-101",
                "Maintenance Type": "Routine Inspection",
                "Maintenance Date": "2026-08-01",
                "Maintenance Status": "Completed",
                "Maintenance Notes": "Routine service completed",
                "Operating Hours": 3500,
                "Downtime": 2.5,
                "Availability (%)": 93.1,
                "Next Maintenance Date": "2026-09-15",
                "Overdue": False,
            },
            {
                "Equipment Name": "Excavator 2",
                "Equipment ID": "EQ-205",
                "Maintenance Type": "Preventive Maintenance",
                "Maintenance Date": "2026-08-05",
                "Maintenance Status": "Overdue",
                "Maintenance Notes": "Tyre replacement pending",
                "Operating Hours": 4800,
                "Downtime": 8.0,
                "Availability (%)": 77.4,
                "Next Maintenance Date": "2026-07-28",
                "Overdue": True,
            },
        ]
    )


def make_default_risks():
    return pd.DataFrame(
        [
            {
                "Hazard": "Loose rock fall",
                "Location": "Pit B",
                "Likelihood": 3,
                "Consequence": 4,
                "Risk Score": 12,
                "Risk Level": "High",
            },
            {
                "Hazard": "Poor ventilation",
                "Location": "South shaft",
                "Likelihood": 2,
                "Consequence": 5,
                "Risk Score": 10,
                "Risk Level": "High",
            },
        ]
    )


def make_default_accounts():
    return pd.DataFrame(
        [
            {"username": "admin", "password": "admin@khwezi", "role": "Administrator"},
            {"username": "safety", "password": "safety@khwezi", "role": "Safety Officer"},
            {"username": "engineer", "password": "engineer@khwezi", "role": "Mining Engineer"},
            {"username": "maintenance", "password": "maintenance@khwezi", "role": "Maintenance Engineer"},
            {"username": "manager", "password": "manager@khwezi", "role": "Manager"},
        ]
    )


# =========================
# Data file utilities
# =========================
def ensure_file(path, default_df):
    if not os.path.exists(path):
        default_df.to_csv(path, index=False)


def load_data(path, default_df):
    ensure_file(path, default_df)
    try:
        df = pd.read_csv(path)
        return df
    except Exception:
        return default_df.copy()


def to_dataframe(value, default_df):
    if value is None:
        return default_df.copy()
    if isinstance(value, pd.DataFrame):
        return value
    if isinstance(value, list):
        return pd.DataFrame(value)
    if isinstance(value, dict):
        return pd.DataFrame([value])
    return pd.DataFrame(value)


# =========================
# Session setup
# =========================
ROLE_PAGES = {
    "Administrator": ["Dashboard", "Worker Safety", "Safety Incidents", "Equipment Monitoring", "Maintenance", "Risk Assessment", "Alerts", "Data Analysis"],
    "Safety Officer": ["Dashboard", "Worker Safety", "Safety Incidents", "Risk Assessment", "Alerts"],
    "Mining Engineer": ["Dashboard", "Worker Safety", "Safety Incidents", "Equipment Monitoring", "Maintenance", "Risk Assessment", "Alerts"],
    "Maintenance Engineer": ["Dashboard", "Equipment Monitoring", "Maintenance", "Alerts"],
    "Manager": ["Dashboard", "Worker Safety", "Safety Incidents", "Equipment Monitoring", "Maintenance", "Risk Assessment", "Alerts", "Data Analysis"],
}


def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "role" not in st.session_state:
        st.session_state.role = ""
    if "welcome_seen" not in st.session_state:
        st.session_state.welcome_seen = False

    if "accounts" not in st.session_state:
        st.session_state.accounts = load_data(ACCOUNTS_FILE, make_default_accounts())
    else:
        st.session_state.accounts = to_dataframe(st.session_state.accounts, make_default_accounts())

    if "workers" not in st.session_state:
        st.session_state.workers = load_data(WORKERS_FILE, make_default_workers())
    else:
        st.session_state.workers = to_dataframe(st.session_state.workers, make_default_workers())

    if "incidents" not in st.session_state:
        st.session_state.incidents = load_data(INCIDENTS_FILE, make_default_incidents())
    else:
        st.session_state.incidents = to_dataframe(st.session_state.incidents, make_default_incidents())

    if "equipment" not in st.session_state:
        st.session_state.equipment = load_data(EQUIPMENT_FILE, make_default_equipment())
    else:
        st.session_state.equipment = to_dataframe(st.session_state.equipment, make_default_equipment())

    if "maintenance" not in st.session_state:
        st.session_state.maintenance = load_data(MAINTENANCE_FILE, make_default_maintenance())
    else:
        st.session_state.maintenance = to_dataframe(st.session_state.maintenance, make_default_maintenance())

    if "risks" not in st.session_state:
        st.session_state.risks = load_data(RISK_FILE, make_default_risks())
    else:
        st.session_state.risks = to_dataframe(st.session_state.risks, make_default_risks())


init_session_state()

# =========================
# UI helpers
# =========================
def show_alert_box(msg, kind="info"):
    color_class = {
        "info": "info-box",
        "success": "success-box",
        "warning": "warning-box",
        "danger": "danger-box",
    }.get(kind, "info-box")
    st.markdown(f'<div class="{color_class}">{msg}</div>', unsafe_allow_html=True)


# =========================
# Welcome page
# =========================
def welcome_page():
    st.markdown(
        """
        <div class="hero">
            <div class="small-label">Khwezi Mining Safety Platform</div>
            <h1>SafeMine360</h1>
            <p>Health, safety and equipment monitoring for a modern mining operation.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="glass-card">
                <div class="small-label">Safety</div>
                <div style="font-size: 2.2rem; margin-top: 0.5rem;">🛡️</div>
                <div style="font-size: 1.02rem; margin-top: 0.6rem; color: #e2e8f0;">Track incidents, near misses and compliance.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="glass-card">
                <div class="small-label">Operations</div>
                <div style="font-size: 2.2rem; margin-top: 0.5rem;">⛏️</div>
                <div style="font-size: 1.02rem; margin-top: 0.6rem; color: #e2e8f0;">Monitor equipment usage and maintenance needs.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="glass-card">
                <div class="small-label">Risk</div>
                <div style="font-size: 2.2rem; margin-top: 0.5rem;">📊</div>
                <div style="font-size: 1.02rem; margin-top: 0.6rem; color: #e2e8f0;">Use data-driven decisions to reduce exposure.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Get Started", use_container_width=True):
        st.session_state.welcome_seen = True
        st.rerun()


# =========================
# Login screen
# =========================
def login_page():
    st.markdown(
        """
        <div class="hero">
            <div class="small-label">Secure access</div>
            <h1>Login</h1>
            <p>Welcome back to the Khwezi mining safety dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            login_submit = st.form_submit_button("Login")

        if login_submit:
            if username.strip() == "":
                st.error("Please enter a username.")
            else:
                account_match = st.session_state.accounts[
                    st.session_state.accounts["username"].astype(str).str.strip().str.lower() == username.strip().lower()
                ]
                if account_match.empty:
                    st.error("Invalid username and/or password.")
                elif str(account_match.iloc[0]["password"]).strip() != password:
                    st.error("Invalid username and/or password.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.username = str(account_match.iloc[0]["username"]).strip()
                    st.session_state.role = str(account_match.iloc[0]["role"]).strip()
                    st.success(f"Welcome back, {st.session_state.username}!")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("signup_form"):
            new_username = st.text_input("New username", key="signup_username", placeholder="Choose a username")
            new_password = st.text_input("Create password", type="password", key="signup_password", placeholder="Create a password")
            new_role = st.selectbox(
                "Role",
                ["Administrator", "Safety Officer", "Mining Engineer", "Maintenance Engineer", "Manager"],
                key="signup_role",
            )
            signup_submit = st.form_submit_button("Create Account")

        if signup_submit:
            cleaned_username = new_username.strip()
            if cleaned_username == "":
                st.error("Please choose a valid username.")
            elif new_password.strip() == "":
                st.error("Please create a password.")
            elif not st.session_state.accounts["username"].astype(str).str.strip().str.lower().isin([cleaned_username.lower()]).any():
                new_account = pd.DataFrame([
                    {"username": cleaned_username, "password": new_password.strip(), "role": new_role}
                ])
                st.session_state.accounts = pd.concat([st.session_state.accounts, new_account], ignore_index=True)
                st.session_state.accounts.to_csv(ACCOUNTS_FILE, index=False)
                st.success("Account created successfully. You can now log in.")
            else:
                st.error("That username already exists. Please choose another one.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='glass-card' style='max-width: 760px;'>
            <div class='small-label'>Demo Accounts</div>
            <div style='margin-top: 0.8rem; color: #e2e8f0; line-height: 1.9;'>
                <strong>admin</strong> / admin@khwezi<br>
                <strong>safety</strong> / safety@khwezi<br>
                <strong>engineer</strong> / engineer@khwezi<br>
                <strong>maintenance</strong> / maintenance@khwezi<br>
                <strong>manager</strong> / manager@khwezi
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# Dashboard
# =========================
def dashboard_page():
    workers_df = st.session_state.workers
    incidents_df = st.session_state.incidents
    equipment_df = st.session_state.equipment
    maintenance_df = st.session_state.maintenance
    risks_df = st.session_state.risks

    total_workers = len(workers_df)
    total_incidents = len(incidents_df)
    total_equipment = len(equipment_df)
    open_incidents = int((incidents_df["Incident Status"] != "Resolved").sum()) if not incidents_df.empty else 0

    near_misses = 0
    if not incidents_df.empty and "Incident Type" in incidents_df.columns:
        near_misses = int(incidents_df[incidents_df["Incident Type"].astype(str).str.contains("Near Miss", case=False, na=False)].shape[0])

    ppe_compliant = 0
    if not workers_df.empty and "PPE Compliance" in workers_df.columns:
        ppe_compliant = int(workers_df["PPE Compliance"].astype(str).str.lower().isin(["compliant", "yes", "true"]).sum())
    ppe_percent = (ppe_compliant / total_workers) * 100 if total_workers else 0

    equipment_alerts = 0
    critical_equipment_alerts = 0
    if not equipment_df.empty:
        for _, eq in equipment_df.iterrows():
            temperature = float(eq.get("Temperature", 0) or 0)
            vibration = float(eq.get("Vibration", 0) or 0)
            temperature_alert = temperature >= 80
            vibration_alert = vibration >= 5
            repair_alert = any(eq.get(col) == "Needs Repair" for col in ["Brakes", "Tyres", "Engine"])
            maint_alert = str(eq.get("Maintenance Status", "")).lower() in ["due", "overdue"]
            if temperature_alert or vibration_alert or repair_alert or maint_alert:
                equipment_alerts += 1
            if temperature > 100 or vibration > 8:
                critical_equipment_alerts += 1

    equipment_under_maintenance = 0
    if not equipment_df.empty and "Maintenance Status" in equipment_df.columns:
        equipment_under_maintenance = int(equipment_df["Maintenance Status"].astype(str).str.lower().str.contains("maint", case=False, na=False).sum())

    avg_availability = 0.0
    if not maintenance_df.empty and "Availability (%)" in maintenance_df.columns:
        avg_availability = float(pd.to_numeric(maintenance_df["Availability (%)"], errors="coerce").mean())

    high_risk = 0
    if not risks_df.empty and "Risk Level" in risks_df.columns:
        high_risk = int(risks_df["Risk Level"].astype(str).str.lower().isin(["high", "critical"]).sum())

    st.markdown('<div class="section-title">📈 Mining Dashboard</div>', unsafe_allow_html=True)
    st.write("Overview of worker safety, incidents and equipment performance.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Registered Workers", total_workers)
    with c2:
        st.metric("Safety Incidents", total_incidents)
    with c3:
        st.metric("Near Misses", near_misses)

    c4, c5, c6 = st.columns(3)
    with c4:
        st.metric("Open Incidents", open_incidents)
    with c5:
        st.metric("Equipment Records", total_equipment)
    with c6:
        st.metric("Equipment Alerts", equipment_alerts)

    c7, c8, c9 = st.columns(3)
    with c7:
        st.metric("PPE Compliant", int(ppe_compliant))
    with c8:
        st.metric("PPE Compliance", f"{ppe_percent:.1f}%")
    with c9:
        st.metric("Under Maintenance", int(equipment_under_maintenance))

    c10, c11 = st.columns(2)
    with c10:
        st.metric("Avg. Equipment Availability", f"{avg_availability:.1f}%")
    with c11:
        st.metric("High-Risk Observations", int(high_risk))

    st.metric("Critical Equipment Alerts", int(critical_equipment_alerts))

    st.markdown("---")
    st.subheader("Safety Incident Overview")
    if not incidents_df.empty and "Severity" in incidents_df.columns:
        st.bar_chart(incidents_df["Severity"].value_counts())
    else:
        st.info("No safety incident data available.")

    st.markdown("---")
    st.subheader("Department Summary")
    if not workers_df.empty and "Department" in workers_df.columns:
        st.bar_chart(workers_df["Department"].value_counts())
    else:
        st.info("No department data available.")


# =========================
# Worker safety page
# =========================
def worker_safety_page():
    st.markdown('<div class="section-title">👷 Worker Safety</div>', unsafe_allow_html=True)

    with st.form("worker_form"):
        col1, col2 = st.columns(2)
        with col1:
            worker_name = st.text_input("Worker Name")
            worker_id = st.text_input("Worker ID")
            department = st.selectbox("Department", ["Mining", "Engineering", "Geology", "Safety"])
            training = st.selectbox("Safety Training Status", ["Completed", "Pending"])
            job_role = st.text_input("Job Role")
        with col2:
            shift = st.selectbox("Shift", ["Day", "Night"])
            ppe = st.selectbox("PPE Compliance", ["Compliant", "Non-compliant"])
            fatigue = st.selectbox("Fatigue Level", ["Low", "Medium", "High"])
            near_misses = st.number_input("Near Misses", min_value=0, step=1)
            previous_incidents = st.number_input("Previous Incidents", min_value=0, step=1)

        safety_observations = st.text_area("Safety Observations")
        submit = st.form_submit_button("Register Worker")

    if submit:
        if not worker_name.strip() or not worker_id.strip():
            st.error("Please enter worker name and worker ID.")
        elif any(str(id_value) == worker_id.strip() for id_value in st.session_state.workers["Worker ID"].astype(str).tolist()):
            st.error("This Worker ID already exists.")
        else:
            risk_score = 0
            if ppe == "Non-compliant":
                risk_score += 2
            if fatigue == "High":
                risk_score += 2
            if near_misses > 0:
                risk_score += 1
            if previous_incidents > 0:
                risk_score += 1

            if risk_score >= 4:
                risk_level = "High"
            elif risk_score >= 2:
                risk_level = "Medium"
            else:
                risk_level = "Low"

            worker = {
                "Name": worker_name.strip(),
                "Worker ID": worker_id.strip(),
                "Department": department,
                "Training Status": training,
                "Job Role": job_role,
                "Shift": shift,
                "PPE Compliance": ppe,
                "Fatigue Level": fatigue,
                "Safety Observations": safety_observations,
                "Near Misses": near_misses,
                "Previous Incidents": previous_incidents,
                "Risk Level": risk_level,
            }

            st.session_state.workers = pd.concat([st.session_state.workers, pd.DataFrame([worker])], ignore_index=True)
            st.session_state.workers.to_csv(WORKERS_FILE, index=False)
            st.success("Worker registered successfully!")

            if risk_level == "High":
                show_alert_box("HIGH RISK: Investigate this worker's safety conditions.", "danger")
            elif risk_level == "Medium":
                show_alert_box("MEDIUM RISK: Review this worker's safety conditions.", "warning")
            else:
                show_alert_box("LOW RISK: No immediate warning from these indicators.", "success")

    st.markdown("---")
    st.subheader("Registered Workers")
    if not st.session_state.workers.empty:
        st.dataframe(st.session_state.workers, use_container_width=True)
    else:
        st.info("No workers registered yet.")


# =========================
# Incidents page
# =========================
def safety_incidents_page():
    st.markdown('<div class="section-title">🚨 Safety Incidents</div>', unsafe_allow_html=True)

    with st.form("incident_form"):
        col1, col2 = st.columns(2)
        with col1:
            incident_date = st.date_input("Incident Date")
            incident_time = st.time_input("Incident Time")
            shift = st.selectbox("Shift", ["Day", "Night"])
            location = st.text_input("Incident Location")
            department = st.selectbox("Department", ["Mining", "Engineering", "Geology", "Safety"])
            incident_type = st.selectbox("Incident Type", ["Near Miss", "Unsafe Condition", "Injury", "Equipment Incident", "Other"])
            severity = st.selectbox("Incident Severity", ["Low", "Medium", "High", "Critical"])
        with col2:
            injury_status = st.selectbox("Was anyone injured?", ["No", "Yes"])
            lost_time = st.selectbox("Lost-Time Injury?", ["No", "Yes"])
            description = st.text_area("Incident Description")
            cause = st.text_area("Incident Cause")
            corrective_action = st.text_area("Corrective Action")
            status = st.selectbox("Incident Status", ["Open", "Under Investigation", "Resolved"])

        submitted = st.form_submit_button("Submit Incident")

    if submitted:
        if not location.strip() or not description.strip():
            st.error("Please enter incident location and description.")
        else:
            existing = st.session_state.incidents
            if existing.empty:
                new_id = 1
            else:
                try:
                    new_id = int(existing["Incident ID"].max()) + 1
                except Exception:
                    new_id = len(existing) + 1

            incident = {
                "Incident ID": new_id,
                "Date": str(incident_date),
                "Time": str(incident_time),
                "Shift": shift,
                "Location": location.strip(),
                "Department": department,
                "Incident Type": incident_type,
                "Severity": severity,
                "Injury Status": injury_status,
                "Lost-Time Injury": lost_time,
                "Description": description.strip(),
                "Cause": cause,
                "Corrective Action": corrective_action,
                "Incident Status": status,
            }
            st.session_state.incidents = pd.concat([existing, pd.DataFrame([incident])], ignore_index=True)
            st.session_state.incidents.to_csv(INCIDENTS_FILE, index=False)
            st.success("Incident recorded successfully!")

    st.markdown("---")
    st.subheader("Saved Safety Incidents")
    if not st.session_state.incidents.empty:
        st.dataframe(st.session_state.incidents, use_container_width=True)
    else:
        st.info("No safety incidents recorded yet.")

    if not st.session_state.incidents.empty:
        st.markdown("---")
        st.subheader("Incident Analysis")
        st.bar_chart(st.session_state.incidents["Severity"].value_counts())
        st.bar_chart(st.session_state.incidents["Incident Type"].value_counts())


# =========================
# Equipment page
# =========================
def equipment_page():
    st.markdown('<div class="section-title">🛠️ Equipment Monitoring</div>', unsafe_allow_html=True)

    with st.form("equipment_form"):
        col1, col2 = st.columns(2)
        with col1:
            equipment_name = st.text_input("Equipment Name")
            equipment_id = st.text_input("Equipment ID")
            equipment_type = st.selectbox("Equipment Type", ["Truck", "Excavator", "Drill", "Loader", "Other"])
            manufacturer = st.text_input("Manufacturer")
            operating_hours = st.number_input("Operating Hours", min_value=0.0, step=1.0)
        with col2:
            temperature = st.number_input("Engine Temperature (°C)", min_value=0.0, step=1.0)
            vibration = st.number_input("Vibration (mm/s)", min_value=0.0, step=0.1)
            fuel_level = st.slider("Fuel Level (%)", 0, 100, 50)
            downtime = st.number_input("Downtime (hours)", min_value=0.0, step=1.0)
            maintenance_status = st.selectbox("Maintenance Status", ["Up to date", "Due", "Overdue", "Under maintenance"])

        brakes = st.selectbox("Brakes", ["Good", "Needs Repair"])
        tyres = st.selectbox("Tyres", ["Good", "Needs Repair"])
        engine = st.selectbox("Engine", ["Good", "Needs Repair"])
        submit = st.form_submit_button("Submit Equipment Report")

    if submit:
        if not equipment_name.strip() or not equipment_id.strip():
            st.error("Please enter equipment name and ID.")
        else:
            record = {
                "Equipment Name": equipment_name.strip(),
                "Equipment ID": equipment_id.strip(),
                "Equipment Type": equipment_type,
                "Manufacturer": manufacturer,
                "Operating Hours": operating_hours,
                "Temperature": temperature,
                "Vibration": vibration,
                "Fuel Level": fuel_level,
                "Brakes": brakes,
                "Tyres": tyres,
                "Engine": engine,
                "Downtime": downtime,
                "Maintenance Status": maintenance_status,
            }
            st.session_state.equipment = pd.concat([st.session_state.equipment, pd.DataFrame([record])], ignore_index=True)
            st.session_state.equipment.to_csv(EQUIPMENT_FILE, index=False)
            st.success("Equipment report submitted successfully!")

    st.markdown("---")
    st.subheader("Equipment Data")
    if not st.session_state.equipment.empty:
        st.dataframe(st.session_state.equipment, use_container_width=True)
    else:
        st.info("No equipment data available yet.")


# =========================
# Maintenance page
# =========================
def maintenance_page():
    st.markdown('<div class="section-title">🔧 Maintenance</div>', unsafe_allow_html=True)

    with st.form("maintenance_form"):
        col1, col2 = st.columns(2)
        with col1:
            eq_name = st.text_input("Equipment Name")
            eq_id = st.text_input("Equipment ID")
            maintenance_type = st.selectbox("Maintenance Type", ["Routine Inspection", "Preventive Maintenance", "Repair"])
            maintenance_date = st.date_input("Maintenance Date")
            status = st.selectbox("Maintenance Status", ["Scheduled", "In Progress", "Completed"])
        with col2:
            notes = st.text_area("Maintenance Notes")
            operating_hours = st.number_input("Operating Hours", min_value=0.0, step=1.0)
            downtime = st.number_input("Downtime (hours)", min_value=0.0, step=1.0)
            next_date = st.date_input("Next Maintenance Date")

        submit = st.form_submit_button("Submit Maintenance Record")

    if submit:
        if not eq_name.strip() or not eq_id.strip():
            st.error("Please enter equipment name and ID.")
        else:
            total = operating_hours + downtime
            availability = (operating_hours / total) * 100 if total > 0 else 0.0
            record = {
                "Equipment Name": eq_name.strip(),
                "Equipment ID": eq_id.strip(),
                "Maintenance Type": maintenance_type,
                "Maintenance Date": str(maintenance_date),
                "Maintenance Status": status,
                "Maintenance Notes": notes,
                "Operating Hours": operating_hours,
                "Downtime": downtime,
                "Availability (%)": round(availability, 1),
                "Next Maintenance Date": str(next_date),
                "Overdue": next_date < pd.Timestamp.today().date() and status != "Completed",
            }
            st.session_state.maintenance = pd.concat([st.session_state.maintenance, pd.DataFrame([record])], ignore_index=True)
            st.session_state.maintenance.to_csv(MAINTENANCE_FILE, index=False)
            st.success("Maintenance record saved successfully!")

    st.markdown("---")
    st.subheader("Maintenance Records")
    if not st.session_state.maintenance.empty:
        st.dataframe(st.session_state.maintenance, use_container_width=True)
    else:
        st.info("No maintenance records available.")


# =========================
# Risk assessment page
# =========================
def risk_assessment_page():
    st.markdown('<div class="section-title">⚠️ Risk Assessment</div>', unsafe_allow_html=True)
    st.write("Assess hazards by multiplying likelihood by consequence.")

    with st.form("risk_form"):
        hazard = st.text_input("Hazard Description")
        location = st.text_input("Hazard Location")
        likelihood = st.selectbox("Likelihood (1 = Rare, 5 = Almost Certain)", [1, 2, 3, 4, 5])
        consequence = st.selectbox("Consequence (1 = Insignificant, 5 = Catastrophic)", [1, 2, 3, 4, 5])
        submit = st.form_submit_button("Save Risk Assessment")

    if submit:
        if not hazard.strip() or not location.strip():
            st.error("Please enter hazard description and location.")
        else:
            risk_score = likelihood * consequence
            if risk_score <= 4:
                risk_level = "Low"
            elif risk_score <= 9:
                risk_level = "Medium"
            elif risk_score <= 16:
                risk_level = "High"
            else:
                risk_level = "Critical"

            record = {
                "Hazard": hazard.strip(),
                "Location": location.strip(),
                "Likelihood": likelihood,
                "Consequence": consequence,
                "Risk Score": risk_score,
                "Risk Level": risk_level,
            }
            st.session_state.risks = pd.concat([st.session_state.risks, pd.DataFrame([record])], ignore_index=True)
            st.session_state.risks.to_csv(RISK_FILE, index=False)
            st.success("Risk assessment saved successfully!")

    st.markdown("---")
    st.subheader("Saved Risk Assessments")
    if not st.session_state.risks.empty:
        st.dataframe(st.session_state.risks, use_container_width=True)
    else:
        st.info("No risk assessments saved yet.")


# =========================
# Alerts page
# =========================
def alerts_page():
    st.markdown('<div class="section-title">🚨 Alerts</div>', unsafe_allow_html=True)

    st.subheader("Equipment Alerts")
    if not st.session_state.equipment.empty:
        for _, eq in st.session_state.equipment.iterrows():
            equipment_name = eq.get("Equipment Name", "Unknown")
            temperature = float(eq.get("Temperature", 0) or 0)
            vibration = float(eq.get("Vibration", 0) or 0)

            if temperature > 100:
                show_alert_box(f"CRITICAL: {equipment_name} engine temperature is too high.", "danger")
            elif temperature >= 80:
                show_alert_box(f"WARNING: {equipment_name} engine temperature is elevated.", "warning")

            if vibration > 8:
                show_alert_box(f"CRITICAL: {equipment_name} vibration is too high.", "danger")
            elif vibration >= 5:
                show_alert_box(f"WARNING: {equipment_name} vibration is elevated.", "warning")

            for field in ["Brakes", "Tyres", "Engine"]:
                if eq.get(field) == "Needs Repair":
                    show_alert_box(f"ALERT: {equipment_name} - {field} needs repair.", "danger")

            if str(eq.get("Maintenance Status", "")).lower() in ["due", "overdue"]:
                show_alert_box(f"ALERT: {equipment_name} maintenance is {eq.get('Maintenance Status')}.", "warning")
    else:
        st.info("No equipment alerts available.")

    st.markdown("---")
    st.subheader("Worker Safety Alerts")
    if not st.session_state.workers.empty:
        for _, worker in st.session_state.workers.iterrows():
            name = worker.get("Name", "Unknown")
            if str(worker.get("PPE Compliance", "")).lower() == "non-compliant":
                show_alert_box(f"ALERT: {name} is not compliant with PPE.", "danger")
            if str(worker.get("Fatigue Level", "")).lower() == "high":
                show_alert_box(f"ALERT: {name} has high fatigue levels.", "warning")
            if str(worker.get("Training Status", "")).lower() == "pending":
                show_alert_box(f"ALERT: {name} has pending safety training.", "warning")
            if str(worker.get("Risk Level", "")).lower() == "high":
                show_alert_box(f"HIGH RISK: {name} requires immediate review.", "danger")
    else:
        st.info("No worker alerts available.")

    st.markdown("---")
    st.subheader("Safety Incident Alerts")
    if not st.session_state.incidents.empty:
        critical = st.session_state.incidents[st.session_state.incidents["Severity"].astype(str).str.lower() == "critical"]
        if not critical.empty:
            show_alert_box(f"CRITICAL ALERT: {len(critical)} critical incident(s) recorded.", "danger")
        open_incidents = st.session_state.incidents[st.session_state.incidents["Incident Status"] != "Resolved"]
        if not open_incidents.empty:
            show_alert_box(f"{len(open_incidents)} incident(s) still require attention.", "warning")
    else:
        st.success("No safety incident alerts.")


# =========================
# Data analysis page
# =========================
def data_analysis_page():
    st.markdown('<div class="section-title">📊 Data Analysis</div>', unsafe_allow_html=True)

    analysis_type = st.selectbox("Choose data to analyze", ["Worker Safety", "Safety Incidents", "Equipment Monitoring", "Risk Assessments"])

    if analysis_type == "Worker Safety":
        if not st.session_state.workers.empty:
            st.metric("Total Workers", len(st.session_state.workers))
            st.bar_chart(st.session_state.workers["Risk Level"].value_counts())
            st.dataframe(st.session_state.workers, use_container_width=True)
        else:
            st.info("No worker records available.")

    elif analysis_type == "Safety Incidents":
        if not st.session_state.incidents.empty:
            st.metric("Total Incidents", len(st.session_state.incidents))
            st.bar_chart(st.session_state.incidents["Severity"].value_counts())
            st.dataframe(st.session_state.incidents, use_container_width=True)
        else:
            st.info("No incident records available.")

    elif analysis_type == "Equipment Monitoring":
        if not st.session_state.equipment.empty:
            st.metric("Total Equipment Records", len(st.session_state.equipment))
            st.bar_chart(st.session_state.equipment["Maintenance Status"].value_counts())
            st.dataframe(st.session_state.equipment, use_container_width=True)
        else:
            st.info("No equipment records available.")

    elif analysis_type == "Risk Assessments":
        if not st.session_state.risks.empty:
            st.metric("Total Risk Assessments", len(st.session_state.risks))
            st.bar_chart(st.session_state.risks["Risk Level"].value_counts())
            st.dataframe(st.session_state.risks, use_container_width=True)
        else:
            st.info("No risk assessments available.")


# =========================
# App flow
# =========================
if not st.session_state.logged_in:
    if not st.session_state.welcome_seen:
        welcome_page()
    else:
        login_page()
    st.stop()

# Logged in layout
st.sidebar.markdown('<div class="small-label">🚧 SafeMine360</div>', unsafe_allow_html=True)
st.sidebar.success(f"Logged in as: {st.session_state.username}")
st.sidebar.write(f"Role: {st.session_state.role}")

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.welcome_seen = False
    st.rerun()

role = st.session_state.role
allowed_pages = ROLE_PAGES.get(role, ["Dashboard"])
page = st.sidebar.selectbox("Choose a page", allowed_pages)

st.title("🏭 Khwezi Mining Health, Safety & Equipment Monitoring")

if page == "Dashboard":
    dashboard_page()
elif page == "Worker Safety":
    worker_safety_page()
elif page == "Safety Incidents":
    safety_incidents_page()
elif page == "Equipment Monitoring":
    equipment_page()
elif page == "Maintenance":
    maintenance_page()
elif page == "Risk Assessment":
    risk_assessment_page()
elif page == "Alerts":
    alerts_page()
elif page == "Data Analysis":
    data_analysis_page()
