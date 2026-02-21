import json
import hashlib
import urllib.parse
import urllib.request
import streamlit as st

# ── OAuth endpoints ──────────────────────────────────────────────────────────
GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_URL  = "https://www.googleapis.com/oauth2/v3/userinfo"
SCOPES = "openid email profile"

# ── Helpers ──────────────────────────────────────────────────────────────────

def _cfg(key: str, default: str = "") -> str:
    """Read from st.secrets safely."""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def _get_query_params() -> dict:
    """
    Get query params using the modern API (st.query_params) with a fallback
    to the deprecated experimental version for older Streamlit installs.
    Always returns plain string values (not lists).
    """
    try:
        # Streamlit >= 1.30 — st.query_params is a dict-like object, values are plain strings
        return dict(st.query_params)
    except AttributeError:
        pass
    # Fallback for older Streamlit — returns {key: [value, ...]}
    raw = st.experimental_get_query_params()
    return {k: (v[0] if isinstance(v, list) and v else v) for k, v in raw.items()}


def _clear_query_params():
    """Clear URL query params using the best available API."""
    try:
        st.query_params.clear()
    except AttributeError:
        st.experimental_set_query_params()


def _build_auth_url() -> str:
    """Build the Google OAuth consent-screen URL."""
    params = {
        "client_id":     _cfg("GOOGLE_CLIENT_ID"),
        "redirect_uri":  _cfg("GOOGLE_REDIRECT_URI", "http://localhost:8501"),
        "response_type": "code",
        "scope":         SCOPES,
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    return GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode(params)


def _exchange_code_for_token(code: str) -> dict:
    """POST the auth-code to Google and get an access token back."""
    # Ensure code is always a plain string, never a list
    if isinstance(code, list):
        code = code[0]
    code = str(code).strip()

    data = urllib.parse.urlencode({
        "code":          code,
        "client_id":     _cfg("GOOGLE_CLIENT_ID"),
        "client_secret": _cfg("GOOGLE_CLIENT_SECRET"),
        "redirect_uri":  _cfg("GOOGLE_REDIRECT_URI", "http://localhost:8501"),
        "grant_type":    "authorization_code",
    }).encode()

    req = urllib.request.Request(
        GOOGLE_TOKEN_URL, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        st.error(f"Google token error body: {error_body}")
        raise


def _fetch_user_info(access_token: str) -> dict:
    """Call Google's userinfo endpoint."""
    req = urllib.request.Request(
        GOOGLE_USER_URL,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _upsert_google_user(google_id: str, email: str, name: str,
                         picture: str, role: str = "student") -> dict:
    from app import get_conn, hash_pw

    fake_pw = hash_pw(f"google-oauth-{google_id}")
    conn    = get_conn()
    c       = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS google_accounts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER UNIQUE NOT NULL,
            google_id   TEXT UNIQUE NOT NULL,
            email       TEXT,
            picture_url TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()

    row = c.execute(
        "SELECT user_id FROM google_accounts WHERE google_id=?", (google_id,)
    ).fetchone()

    if row:
        user_id = row[0]
        c.execute("UPDATE users SET name=? WHERE id=?", (name, user_id))
        c.execute(
            "UPDATE google_accounts SET email=?, picture_url=? WHERE google_id=?",
            (email, picture, google_id)
        )
        conn.commit()
    else:
        base_uname = email.split("@")[0].replace(".", "_").lower()
        username   = base_uname
        suffix     = 1
        while c.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
            username = f"{base_uname}_{suffix}"; suffix += 1

        c.execute(
            "INSERT INTO users (username, password, role, name) VALUES (?,?,?,?)",
            (username, fake_pw, role, name)
        )
        user_id = c.lastrowid
        c.execute(
            "INSERT INTO google_accounts (user_id, google_id, email, picture_url) VALUES (?,?,?,?)",
            (user_id, google_id, email, picture)
        )
        conn.commit()

    user_row = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()

    if user_row:
        d = dict(user_row)
        d["picture"] = picture
        return d
    return {}


# ── Main entry point ─────────────────────────────────────────────────────────

def handle_google_auth(default_role: str = "student") -> bool:
    if not _cfg("GOOGLE_CLIENT_ID"):
        return False

    # Guard: don't re-process if user already logged in
    if st.session_state.get("user"):
        return False

    params = _get_query_params()

    if "code" not in params:
        return False

    # ── Extract the raw code string ──────────────────────────────────────────
    code = params["code"]
    if isinstance(code, list):
        code = code[0]
    code = str(code).strip()

    if not code:
        return False

    # Prevent processing the same code twice (Streamlit reruns can re-trigger this)
    if st.session_state.get("_processed_oauth_code") == code:
        return False
    st.session_state["_processed_oauth_code"] = code

    try:
        token_data   = _exchange_code_for_token(code)
        access_token = token_data.get("access_token", "")
        if not access_token:
            st.error("⚠️ Google login failed — no access token received.")
            _clear_query_params()
            return False

        user_info = _fetch_user_info(access_token)
        google_id = user_info.get("sub", "")
        email     = user_info.get("email", "")
        name      = user_info.get("name", email)
        picture   = user_info.get("picture", "")

        if not google_id:
            st.error("⚠️ Could not retrieve Google account details.")
            _clear_query_params()
            return False

        user = _upsert_google_user(google_id, email, name, picture, default_role)
        if user:
            st.session_state.user = user
            st.session_state.pop("_processed_oauth_code", None)
            try:
                from app import save_session
                save_session(user["id"])
            except Exception:
                pass
            _clear_query_params()
            return True

    except Exception as exc:
        import traceback
        st.error(f"⚠️ Google authentication error: {exc}")
        st.code(traceback.format_exc())
        st.session_state.pop("_processed_oauth_code", None)

    _clear_query_params()
    return False


def google_login_button(label: str = "🔵 Continue with Google",
                         role_hint: str = "student"):
    if not _cfg("GOOGLE_CLIENT_ID"):
        st.warning("⚠️ Google OAuth not configured. Add GOOGLE_CLIENT_ID, "
                   "GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI to secrets.toml.")
        return

    st.session_state["_google_role_hint"] = role_hint
    auth_url = _build_auth_url()

    st.markdown(f"""
<div style="display:flex; justify-content:center; margin:10px 0;">
    <a href="{auth_url}" target="_self" style="
        display:inline-flex; align-items:center; gap:10px;
        background:#fff; color:#3c4043; border:1px solid #dadce0;
        border-radius:8px; padding:10px 24px;
        font-size:0.92rem; font-weight:600; text-decoration:none;
        box-shadow:0 1px 3px rgba(0,0,0,0.15);
        cursor:pointer;
    ">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
             width="20" height="20"/>
        {label}
    </a>
</div>
""", unsafe_allow_html=True)