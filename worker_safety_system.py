import os
import pandas as pd

# ==========================================
# DATABASE FILE PATHS
# ==========================================
WORKER_DB = "worker_safety.csv"
INCIDENT_DB = "safety_incidents.csv"


# ==========================================
# 1. DATABASE INITIALISATION
# ==========================================
def init_safety_databases():
    """Initialises worker safety and incident CSV databases with required schema columns."""
    if not os.path.exists(WORKER_DB):
        worker_cols = [
            "Worker ID",
            "Department",
            "Job Role",
            "Shift",
            "PPE Compliance",
            "Safety Training Status",
            "Fatigue Level",
            "Safety Observations",
            "Near Misses",
            "Risk Level",
        ]
        pd.DataFrame(columns=worker_cols).to_csv(WORKER_DB, index=False)

    if not os.path.exists(INCIDENT_DB):
        incident_cols = [
            "Incident ID",
            "Date",
            "Shift",
            "Department",
            "Location",
            "Incident Type",
            "Severity",
            "Likelihood",
            "Risk Score",
            "Risk Level",
            "Injury Status",
            "LTI Status",
            "Cause",
            "Corrective Action",
            "Incident Status",
        ]
        pd.DataFrame(columns=incident_cols).to_csv(INCIDENT_DB, index=False)


# ==========================================
# 2. ROLE-BASED ACCESS CONTROL (TABLE 1 RBAC)
# ==========================================
def check_safety_access(user_role: str) -> bool:
    """Enforces Table 1 Role-Based Access Control (RBAC).

    Authorized: Administrator, Safety Officer, Mining Engineer, Manager.
    Denied: Maintenance Engineer, General Worker.
    """
    authorized_roles = [
        "Administrator",
        "Safety Officer",
        "Mining Engineer",
        "Manager",
    ]
    return user_role.strip().title() in authorized_roles


# ==========================================
# 3. SAFETY INCIDENT LOGGING & RISK MATRIX
# ==========================================
def log_safety_incident(user_role: str, incident_data: dict):
    """Logs safety incidents, evaluates risk score (Likelihood x Consequence),
    triggers critical alerts (Score >= 10), and appends data using pandas.
    """
    # Step 1: Enforce RBAC Permission Check
    if not check_safety_access(user_role):
        return (
            False,
            "Access Denied: Role not authorized to access Safety Database.",
        )

    # Step 2: Validate Numeric Inputs (1 to 5 scale)
    try:
        likelihood = int(incident_data["likelihood"])
        consequence = int(incident_data["severity"])
        if not (1 <= likelihood <= 5 and 1 <= consequence <= 5):
            return (
                False,
                "Validation Error: Likelihood and Severity must be between 1 and 5.",
            )
    except (ValueError, KeyError):
        return (
            False,
            "Validation Error: Numeric inputs required for Risk Score calculation.",
        )

    # Step 3: Compute 5x5 Risk Score (Likelihood x Consequence)
    risk_score = likelihood * consequence

    # Step 4: Classify Risk Level Boundaries
    if risk_score >= 17:
        risk_level = "Critical"
    elif risk_score >= 10:
        risk_level = "High"
    elif risk_score >= 5:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Step 5: Construct 15-Variable Incident Record
    record = {
        "Incident ID": incident_data.get("incident_id", "INC-001"),
        "Date": incident_data.get("date", "2026-10-26"),
        "Shift": incident_data.get("shift", "Day"),
        "Department": incident_data.get("department", "Extraction"),
        "Location": incident_data.get("location", "Underground Stope A"),
        "Incident Type": incident_data.get("incident_type", "Near Miss"),
        "Severity": consequence,
        "Likelihood": likelihood,
        "Risk Score": risk_score,
        "Risk Level": risk_level,
        "Injury Status": incident_data.get("injury_status", "None"),
        "LTI Status": incident_data.get("lti_status", "No"),
        "Cause": incident_data.get("cause", "Unspecified"),
        "Corrective Action": incident_data.get(
            "action", "Inspect area and apply safety control"
        ),
        "Incident Status": "Open",
    }

    # Step 6: Ensure Databases Exist & Append Record to CSV
    init_safety_databases()
    df = pd.read_csv(INCIDENT_DB)
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(INCIDENT_DB, index=False)

    # Step 7: Evaluate High/Critical Alert Trigger (Risk Score >= 10)
    alert_triggered = risk_score >= 10

    return True, {"record": record, "alert": alert_triggered}


# ==========================================
# 4. WORKER FATIGUE & PPE CHECK
# ==========================================
def check_worker_fatigue(fatigue_level: int, ppe_compliance: bool) -> dict:
    """Evaluates field worker fatigue level and PPE compliance for safety warnings."""
    is_unsafe = fatigue_level > 3 or not ppe_compliance

    if fatigue_level > 3 and not ppe_compliance:
        warning_msg = (
            "CRITICAL FIELD WARNING: High Worker Fatigue & Non-Compliant PPE!"
        )
    elif fatigue_level > 3:
        warning_msg = (
            "FATIGUE ALERT: Worker Fatigue Level exceeds safety limit (>3)."
        )
    elif not ppe_compliance:
        warning_msg = "SAFETY VIOLATION: Mandatory PPE equipment missing."
    else:
        warning_msg = "Field Worker Status Normal."

    return {
        "unsafe": is_unsafe,
        "fatigue_level": fatigue_level,
        "ppe_compliance": ppe_compliance,
        "message": warning_msg,
    }


# ==========================================
# 5. DATA ANALYTICS & DASHBOARD KPIS
# ==========================================
def filter_incidents_by_department(dept_name: str) -> pd.DataFrame:
    """Filters incident data by department to answer Appendix A analytics queries."""
    init_safety_databases()
    df = pd.read_csv(INCIDENT_DB)
    if df.empty:
        return df
    return df[df["Department"].str.lower() == dept_name.lower()]


def get_safety_kpis() -> dict:
    """Calculates key safety summary metrics for Student D's Streamlit dashboard."""
    init_safety_databases()
    df = pd.read_csv(INCIDENT_DB)

    if df.empty:
        return {
            "total_incidents": 0,
            "critical_alerts": 0,
            "lti_count": 0,
            "open_incidents": 0,
        }

    return {
        "total_incidents": len(df),
        "critical_alerts": len(df[df["Risk Score"] >= 10]),
        "lti_count": len(df[df["LTI Status"].str.upper() == "YES"]),
        "open_incidents": len(
            df[df["Incident Status"].str.title() == "Open"]
        ),
    }


# ==========================================
# 6. LOCAL TEST EXECUTION BLOCK
# ==========================================
if __name__ == "__main__":
    print("--------------------------------------------------")
    print(" TESTING STUDENT A: WORKER SAFETY SYSTEM MODULE")
    print("--------------------------------------------------")

    # Test 1: RBAC Access Check
    print("Testing RBAC Permission for 'Safety Officer':")
    print("Access Granted:", check_safety_access("Safety Officer"))

    print("\nTesting RBAC Permission for 'Maintenance Engineer':")
    print("Access Granted:", check_safety_access("Maintenance Engineer"))

    # Test 2: Logging an Incident with High Risk (Alert Expected)
    sample_incident = {
        "incident_id": "INC-2026-001",
        "date": "2026-10-26",
        "shift": "Night",
        "department": "Underground Extraction",
        "location": "Stope Shaft 4",
        "incident_type": "Rockfall Near Miss",
        "severity": 4,
        "likelihood": 3,
        "injury_status": "None",
        "lti_status": "No",
        "cause": "Loose ground after blasting",
        "action": "Install additional rock bolts and mesh",
    }

    success, result = log_safety_incident("Safety Officer", sample_incident)
    if success:
        print("\nIncident Logged Successfully!")
        print("Calculated Risk Score :", result["record"]["Risk Score"])
        print("Calculated Risk Level :", result["record"]["Risk Level"])
        print("Critical Alert Triggered:", result["alert"])

    # Test 3: Dashboard KPIs
    kpis = get_safety_kpis()
    print("\nCurrent Safety KPIs:", kpis)
    print("--------------------------------------------------")
