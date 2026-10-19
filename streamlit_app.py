import streamlit as st
import pandas as pd
import hashlib
import io
import numpy as np
import plotly.express as px

# -----------------------
# Helper functions
# -----------------------
def hash_password(password: str) -> str:
    """Return the SHA-256 hex digest of the given password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(username: str, password: str) -> bool:
    """Verify password for a given username against the users store."""
    return username in users and users[username] == hash_password(password)

def init_session_state():
    """Initialize needed session state keys."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    if "remember" not in st.session_state:
        st.session_state.remember = False
    if "uploaded_dfs" not in st.session_state:
        # dict: filename -> dataframe
        st.session_state.uploaded_dfs = {}

@st.cache_data
def read_csv_bytes(file_bytes: bytes, **kwargs) -> pd.DataFrame:
    """Read CSV from raw bytes into pandas DataFrame (cached)."""
    return pd.read_csv(io.BytesIO(file_bytes), **kwargs)

def add_uploaded_file(uploaded_file):
    """Add uploaded file to session_state.uploaded_dfs with unique name."""
    try:
        df = read_csv_bytes(uploaded_file.read())
        name = uploaded_file.name
        base = name.rsplit(".", 1)[0]
        ext = name.rsplit(".", 1)[1] if "." in name else "csv"
        final_name = name
        i = 1
        while final_name in st.session_state.uploaded_dfs:
            final_name = f"{base} ({i}).{ext}"
            i += 1
        st.session_state.uploaded_dfs[final_name] = df
        st.success(f"Uploaded: {final_name} — shape: {df.shape}")
    except Exception as e:
        st.error(f"Failed to read {uploaded_file.name}: {e}")

def filter_dataframe(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply numeric and categorical filters to dataframe."""
    out = df.copy()
    for col, cfg in filters.items():
        if cfg["type"] == "numeric":
            lo, hi = cfg["value"]
            out = out[(out[col] >= lo) & (out[col] <= hi)]
        else:
            vals = cfg["value"]
            if vals:
                out = out[out[col].isin(vals)]
    return out

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

# -----------------------
# Example in-memory user store (username -> hashed_password)
# Replace this with a database in production
# -----------------------
users = {
    # passwords: alice -> password123 ; bob -> secret
    "alice": hash_password("password123"),
    "bob": hash_password("secret"),
}

# -----------------------
# App UI & Logic
# -----------------------
st.set_page_config(page_title="My App", page_icon="📊", layout="wide")
init_session_state()

st.title("📊CSV Dashboard — Login required")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
# If already logged in, show dashboard and logout option
if st.session_state.logged_in:
    # Header and logout
    header_cols = st.columns([1, 6, 1])
    with header_cols[0]:
        st.empty()
    with header_cols[1]:
        st.markdown(f"### Logged in as: **{st.session_state.username}**")
    with header_cols[2]:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.login_attempts = 0
            st.session_state.remember = False
            st.experimental_rerun()

    # Sidebar: uploads and settings
    st.sidebar.header("CSV Upload & Files")
    uploaded = st.sidebar.file_uploader(":file_folder: Upload CSV files (multiple allowed)", type=["csv", "xlsx"' "xls"], accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            add_uploaded_file(f)

    if not st.session_state.uploaded_dfs:
        st.sidebar.info("No CSV uploaded. You can upload one or click below to load a sample dataset.")
        if st.sidebar.button("Load sample dataset"):
            sample = pd.DataFrame({
                "sepal_length": np.random.normal(5.8, 0.8, 150),
                "sepal_width": np.random.normal(3.0, 0.4, 150),
                "petal_length": np.random.normal(3.7, 1.5, 150),
                "petal_width": np.random.normal(1.2, 0.8, 150),
                "species": np.random.choice(["setosa", "versicolor", "virginica"], 150)
            })
            st.session_state.uploaded_dfs["sample_iris.csv"] = sample
            st.experimental_rerun()

    st.sidebar.markdown("---")
    st.sidebar.header("Dashboard Settings")
    show_table = st.sidebar.checkbox("Show table", value=True)
    show_summary = st.sidebar.checkbox("Show summary (describe)", value=True)
    show_charts = st.sidebar.checkbox("Show charts", value=True)

    # If there are uploaded CSVs, let the user pick one
    if st.session_state.uploaded_dfs:
        file_list = list(st.session_state.uploaded_dfs.keys())
        selected_file = st.sidebar.selectbox("Select CSV file", options=file_list)
        df = st.session_state.uploaded_dfs[selected_file]

        st.subheader(f"File: {selected_file}")
        st.write(f"Rows: {df.shape[0]} — Columns: {df.shape[1]}")

        # Column info and nulls
        with st.expander("Column info and nulls"):
            info_df = pd.DataFrame({
                "dtype": df.dtypes.astype(str),
                "n_missing": df.isna().sum(),
                "n_unique": df.nunique(dropna=False)
            })
            st.dataframe(info_df)

        # Build filters in sidebar
        st.sidebar.header("Filters")
        filters = {}
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=np.number).columns.tolist()

        # Numeric filters (range sliders)
        for col in numeric_cols:
            try:
                min_val = float(df[col].min())
                max_val = float(df[col].max())
                default_lo = min_val
                default_hi = max_val
                rng = st.sidebar.slider(f"{col} range", min_val, max_val, (default_lo, default_hi), key=f"rng_{selected_file}_{col}")
                filters[col] = {"type": "numeric", "value": rng}
            except Exception:
                # fallback if conversion fails
                filters[col] = {"type": "numeric", "value": (df[col].min(), df[col].max())}

        # Categorical filters (multi-select)
        for col in categorical_cols:
            opts = sorted(df[col].dropna().unique().tolist())
            sel = st.sidebar.multiselect(f"Filter {col}", options=opts, default=opts, key=f"ms_{selected_file}_{col}")
            filters[col] = {"type": "categorical", "value": sel}

        # Apply filters
        filtered_df = filter_dataframe(df, filters)

        # Table and download
        if show_table:
            st.markdown("### Data (filtered)")
            n_display = st.selectbox("Rows to show", options=[5, 10, 25, 50, 100], index=1, key="n_display")
            st.dataframe(filtered_df.head(n_display))

            csv_bytes = df_to_csv_bytes(filtered_df)
            st.download_button("Download filtered CSV", data=csv_bytes, file_name=f"filtered_{selected_file}", mime="text/csv")

        # Summary
        if show_summary:
            st.markdown("### Summary statistics")
            try:
                st.dataframe(filtered_df.describe(include="all").T)
            except Exception:
                st.write("Unable to compute describe for this dataset.")

        # Charts
        if show_charts:
            st.markdown("### Charts")
            chart_col1, chart_col2 = st.columns([2, 1])

            with chart_col2:
                chart_type = st.selectbox("Chart type", ["Histogram", "Scatter", "Box", "Correlation heatmap"], key="chart_type")
                if chart_type in ["Histogram", "Box"]:
                    sel_col = st.selectbox("Column", options=df.columns.tolist(), index=0, key="sel_col")
                elif chart_type == "Scatter":
                    x_col = st.selectbox("X column", options=df.columns.tolist(), index=0, key="xcol")
                    y_col = st.selectbox("Y column", options=df.columns.tolist(), index=1 if len(df.columns) > 1 else 0, key="ycol")
                    color_col = st.selectbox("Color (optional)", options=[None] + df.columns.tolist(), index=0, key="colorcol")
                else:
                    # heatmap requires no extra selection
                    pass

            with chart_col1:
                try:
                    if chart_type == "Histogram":
                        if pd.api.types.is_numeric_dtype(filtered_df[sel_col]):
                            fig = px.histogram(filtered_df, x=sel_col, nbins=30, title=f"Histogram of {sel_col}")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Selected column is not numeric for histogram.")
                    elif chart_type == "Box":
                        if pd.api.types.is_numeric_dtype(filtered_df[sel_col]):
                            fig = px.box(filtered_df, y=sel_col, points="outliers", title=f"Box plot of {sel_col}")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Selected column is not numeric for box plot.")
                    elif chart_type == "Scatter":
                        fig = px.scatter(
                            filtered_df,
                            x=x_col,
                            y=y_col,
                            color=color_col if color_col else None,
                            title=f"Scatter: {x_col} vs {y_col}",
                            trendline="ols" if pd.api.types.is_numeric_dtype(filtered_df[x_col]) and pd.api.types.is_numeric_dtype(filtered_df[y_col]) else None
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    elif chart_type == "Correlation heatmap":
                        numeric = filtered_df.select_dtypes(include=np.number)
                        if numeric.shape[1] >= 2:
                            corr = numeric.corr()
                            fig = px.imshow(corr, text_auto=True, title="Correlation matrix")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Need at least two numeric columns for correlation heatmap.")
                except Exception as e:
                    st.error(f"Error creating chart: {e}")

        # Quick actions
        st.markdown("### Quick actions")
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        with quick_col1:
            if st.button("Show head", key="btn_head"):
                st.write(filtered_df.head(10))
        with quick_col2:
            if st.button("Show tail", key="btn_tail"):
                st.write(filtered_df.tail(10))
        with quick_col3:
            if st.button("Clear uploaded files", key="btn_clear"):
                st.session_state.uploaded_dfs = {}
                st.experimental_rerun()

else:
    # Not logged in: show login form
    st.subheader("Please log in")
    MAX_ATTEMPTS = 5
    if st.session_state.login_attempts >= MAX_ATTEMPTS:
        st.error("Too many failed login attempts. Try again later.")
    else:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            remember = st.checkbox("Remember me")
            submitted = st.form_submit_button("Login")

        if submitted:
            if not username or not password:
                st.warning("Please enter both username and password.")
            else:
                if verify_password(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.remember = remember
                    st.session_state.login_attempts = 0
                    st.experimental_rerun()
                else:
                    st.session_state.login_attempts += 1
                    attempts_left = MAX_ATTEMPTS - st.session_state.login_attempts
                    st.error(f"Login failed. Attempts left: {attempts_left}")

# Optional: quick debug view (remove in production)
if st.checkbox("Show session state (debug)", value=False):
    def format_state(v):
        if isinstance(v, dict):
            return {k: str(vv.shape) if isinstance(vv, pd.DataFrame) else str(vv) for k, vv in v.items()}
        return str(v)
    st.json({k: format_state(v) for k, v in st.session_state.items()})
