"""
scraper2.py — Method 2 panel scraper for bot.py

Uses httpx.AsyncClient with follow_redirects=True — the proven approach from
the backup bot. httpx correctly handles all panel login redirects including IMS
which previously had CDR redirect issues with requests.Session.

No panels are hardcoded. All panels come from bot_settings["panels"] via get_settings().
Runs in a dedicated background thread with its own asyncio event loop.

Called by bot.py:
    import scraper2
    scraper2.start(on_otp_found=callback, get_settings=lambda: bot_settings)

Callback signature:
    def on_otp_found(num: str, otp: str, msg_text: str, panel_name: str): ...
"""

import asyncio
import hashlib
import re
import threading
from datetime import datetime, timedelta
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

# ─── Globals ─────────────────────────────────────────────────────────────────

_on_otp_found  = None
_get_settings  = None
_processed     = set()
_proc_lock     = threading.Lock()
_loop          = None
_FETCH_INTERVAL = 3     # seconds between polls per panel

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ─── OTP extraction (mirrors bot.py's extract_otp_code) ──────────────────────

def _extract_otp(text: str):
    if not text:
        return None
    clean = re.sub(r"[\u200B-\u200D\uFEFF]", "", str(text))
    # 1. Multi-part OTPs (e.g. 123-456 or 80-97-61)
    multi = re.search(r"(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})", clean)
    if multi:
        return multi.group(0).replace(" ", "")
    # 2. Keyword-based
    kws = ["code", "is", "otp", "pin", "verification", "auth", "رمز", "your code"]
    kp  = "|".join(kws)
    m = re.search(rf"(?:{kp})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})", clean, re.I)
    if m and m.group(1).isdigit():
        return m.group(1)
    m2 = re.search(rf"([a-z0-9]{{4,10}})\s*(?:is your|is the|)", clean, re.I)
    if m2 and m2.group(1).isdigit():
        return m2.group(1)
    # 3. Google OTP
    gm = re.search(r"G-(\d{6})", clean, re.IGNORECASE)
    if gm:
        return gm.group(1)
    # 4. Digit fallback
    digits = re.findall(r"(?<!\d)\d{4,8}(?!\d)", clean)
    if digits:
        return digits[0]
    return None

# ─── Dedup ───────────────────────────────────────────────────────────────────

def _dedup_key(tag: str, num: str, otp: str) -> str:
    return hashlib.md5(f"{tag}|{num}|{otp}".encode()).hexdigest()

def _is_processed(key: str) -> bool:
    with _proc_lock:
        return key in _processed

def _mark_processed(key: str):
    with _proc_lock:
        _processed.add(key)
        if len(_processed) > 10000:
            _processed.clear()

# ─── Login page detection ─────────────────────────────────────────────────────

def _is_login_page(html: str, url: str = "") -> bool:
    if re.search(r"/(login|signin|sign-in|logon)(/|$|\?)", url.lower()):
        return True
    soup = BeautifulSoup(html, "html.parser")
    if soup.find("input", {"type": "password"}):
        return True
    title = soup.find("title")
    if title and any(w in title.get_text().lower() for w in ["login", "sign in", "log in"]):
        return True
    body = html.lower()
    for phrase in ["session expired", "please login", "please log in",
                   "please sign in", "unauthorized", "login required"]:
        if phrase in body:
            return True
    return False

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _solve_math_captcha(expr: str) -> str:
    expr = expr.replace("×", "*").replace("x", "*").replace("÷", "/")
    try:
        return str(int(eval(expr)))  # noqa: S307
    except Exception:
        return "0"

def _extract_csrf(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", {"name": "csrf-token"})
    if meta and meta.get("content"):
        return meta["content"]
    hidden = soup.find("input", {"name": re.compile(r"_token|csrf|authenticity_token", re.I)})
    if hidden and hidden.get("value"):
        return hidden["value"]
    return ""

def _build_ajax_url(base: str, role: str, records: int = 200) -> str:
    today    = datetime.now().strftime("%Y-%m-%d 00:00:00").replace(" ", "%20")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 23:59:59").replace(" ", "%20")
    api_path = f"/{role}/res/data_smscdr.php"
    return (
        f"{base}{api_path}?fdate1={today}&fdate2={tomorrow}&"
        "frange=&fnum=&fcli=&fgdate=&fgmonth=&fgrange=&fgnumber=&fgcli=&fg=0&"
        f"sEcho=1&iColumns=7&sColumns=%2C%2C%2C%2C%2C%2C&iDisplayStart=0&iDisplayLength={records}&"
        "mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&"
        "mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&"
        "mDataProp_2=2&sSearch_2=&bRegex_2=false&bSearchable_2=true&bSortable_2=true&"
        "mDataProp_3=3&sSearch_3=&bRegex_3=false&bSearchable_3=true&bSortable_3=true&"
        "mDataProp_4=4&sSearch_4=&bRegex_4=false&bSearchable_4=true&bSortable_4=true&"
        "mDataProp_5=5&sSearch_5=&bRegex_5=false&bSearchable_5=true&bSortable_5=true&"
        "mDataProp_6=6&sSearch_6=&bRegex_6=false&bSearchable_6=true&bSortable_6=true&"
        "sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=desc&iSortingCols=1"
    )

# ─── Record parsers ───────────────────────────────────────────────────────────

_SKIP_VALS = {"", "none", "0", "1", "null", "undefined", "n/a", "-"}
_SKIP_RE   = re.compile(
    r"^[\$€£₹¥₩₺₽]?\s*\d*\.?\d*[\$€£₹¥₩₺₽]?$"
    r"|^(delivered|sent|failed|pending|rejected|received|success|error)$",
    re.I,
)

_CLI_KEYS   = ["cli", "client", "service", "app", "provider", "application", "sender_id", "source"]
_NUM_KEYS   = ["destination", "number", "num", "msisdn", "phone", "mobile", "to"]
_MSG_KEYS   = ["message", "msg", "sms", "text", "content", "body"]

def _extract_cli_from_dict(row: dict) -> str:
    """Extract CLI/service name from a dict row, ignoring purely numeric values."""
    lower = {str(k).lower(): v for k, v in row.items()}
    for k in _CLI_KEYS:
        val = str(lower.get(k, "") or "").strip()
        if val and not re.match(r'^\+?[\d\s\-]+$', val):
            return val
    return ""

def _parse_ajax_records(data: dict, p: dict) -> list:
    n_idx = max(0, int(p.get("num_col_idx", 2)) - 1)
    rows  = data.get("aaData") or data.get("data") or []
    out   = []
    for row in rows:
        if isinstance(row, (list, tuple)) and len(row) >= 4:
            dt_str = str(row[0]).strip()
            number = re.sub(r"[^\d]", "", str(row[n_idx] if n_idx < len(row) else row[2]))
            msg    = ""
            cli    = ""
            for i in range(len(row) - 1, 2, -1):
                v = re.sub(r"<[^>]+>", "", str(row[i])).strip()
                if not v or v.lower() in _SKIP_VALS:
                    continue
                if _SKIP_RE.match(v) or len(v) < 3:
                    continue
                # If it looks like a service name (short, no OTP digits) treat as CLI
                if not cli and len(v) <= 30 and not re.search(r'\d{4,}', v):
                    cli = v
                    continue
                msg = v
                break
            if number and msg:
                out.append({"number": number, "message": msg, "datetime": dt_str, "cli": cli})
        elif isinstance(row, dict):
            lower_row = {str(k).lower(): v for k, v in row.items()}
            number = re.sub(r"[^\d]", "", str(
                next((lower_row[k] for k in _NUM_KEYS if k in lower_row and lower_row[k]), "") or ""))
            message = re.sub(r"<[^>]+>", "", str(
                next((lower_row[k] for k in _MSG_KEYS if k in lower_row and lower_row[k]), "") or "")).strip()
            dt_str  = str(row.get("datetime") or row.get("date") or "").strip()
            cli     = _extract_cli_from_dict(row)
            if number and message:
                out.append({"number": number, "message": message, "datetime": dt_str, "cli": cli})
    return out

_CLI_COL_NAMES = ["cli", "client", "service", "app", "provider", "application", "sender", "source"]

def _parse_html_records(html: str, p: dict) -> list:
    n_col = p.get("num_col_name", "number").lower()
    m_col = p.get("msg_col_name", "message").lower()
    n_idx = max(0, int(p.get("num_col_idx", 2)) - 1)
    m_idx = max(0, int(p.get("msg_col_idx", 4)) - 1)
    soup  = BeautifulSoup(html, "html.parser")
    out   = []
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue
        fn, fm, fc = n_idx, m_idx, -1  # fc = cli column index (-1 = not found)
        header_cells = rows[0].find_all(["th", "td"])
        for i, cell in enumerate(header_cells):
            ct = cell.get_text(strip=True).lower()
            if n_col in ct or "number" in ct or "phone" in ct or "msisdn" in ct:
                fn = i
            if m_col in ct or "message" in ct or "sms" in ct or "text" in ct:
                fm = i
            # Detect CLI/service column
            if any(c in ct for c in _CLI_COL_NAMES):
                fc = i
        for row in rows[1:]:
            cols = row.find_all(["td", "th"])
            if len(cols) <= max(fn, fm):
                continue
            number  = re.sub(r"[^\d]", "", cols[fn].get_text(strip=True))
            message = cols[fm].get_text(separator=" ", strip=True)
            # Extract CLI from dedicated column if detected
            cli = ""
            if fc >= 0 and fc < len(cols):
                cli_raw = cols[fc].get_text(strip=True)
                if cli_raw and not re.match(r'^\+?[\d\s\-]+$', cli_raw):
                    cli = cli_raw
            if number and 5 <= len(number) <= 18 and message:
                out.append({"number": number, "message": message, "datetime": "", "cli": cli})
    return out

# ─── Panel session (httpx.AsyncClient — backup-bot proven approach) ───────────

class _PanelSession:
    def __init__(self, idx: int, p: dict):
        self.idx      = idx
        self.p        = p
        self.tag      = (p.get("name") or p.get("type") or f"Panel{idx}").strip()
        self.username = (p.get("username") or p.get("user") or "").strip()
        self.password = (p.get("password") or p.get("pass") or "").strip()
        self.login_url = (p.get("login_url") or "").strip()
        self._client: httpx.AsyncClient | None = None
        self._role    = "client"
        self._sesskey = None
        self._csrf    = None
        self._skip_sesskey = False

    def _base(self) -> str:
        url = self.login_url
        for suffix in ["/login", "/signin", "/sign-in", "/logon", "/auth"]:
            idx = url.lower().find(suffix)
            if idx != -1:
                return url[:idx]
        return url.rstrip("/")

    def _new_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers=_BROWSER_HEADERS.copy(),
        )

    async def login(self) -> bool:
        if not self.login_url or not self.username or not self.password:
            print(f"[S2/{self.tag}] Missing login_url / credentials — skipping")
            return False

        base = self._base()
        login_paths = list(dict.fromkeys(filter(None, [
            self.login_url,
            f"{base}/login",
            f"{base}/signin",
            f"{base}/sign-in",
            f"{base}/client/login",
            f"{base}/agent/login",
        ])))

        client     = self._new_client()
        login_url  = None
        login_resp = None

        try:
            for lpath in login_paths:
                try:
                    resp = await client.get(lpath, timeout=15)
                    if resp.status_code == 200:
                        login_url  = lpath
                        login_resp = resp
                        if _is_login_page(resp.text, str(resp.url)):
                            break
                except Exception:
                    continue

            if login_resp is None:
                print(f"[S2/{self.tag}] ⚠️ Cannot reach panel")
                await client.aclose()
                return False

            soup = BeautifulSoup(login_resp.text, "html.parser")
            form_data: dict = {}
            form_action_url = None

            form   = soup.find("form", {"method": re.compile("post", re.I)}) or soup.find("form")
            inputs = form.find_all("input") if form else soup.find_all("input")

            if form:
                action = form.get("action", "")
                if action:
                    form_action_url = (
                        action if action.startswith("http")
                        else urljoin(base + "/", action.lstrip("/"))
                    )

            # Math captcha
            captcha_answer = None
            mm = re.search(r"(\d+)\s*([\+\-\*×x])\s*(\d+)\s*=\s*\?",
                           login_resp.text, re.I)
            if mm:
                captcha_answer = _solve_math_captcha(
                    f"{mm.group(1)} {mm.group(2)} {mm.group(3)}")
                print(f"[S2/{self.tag}] Captcha: {mm.group(0)} = {captcha_answer}")

            # CSRF
            csrf_inp = soup.find("input",
                                 {"name": re.compile(r"_token|csrf|authenticity_token", re.I)})
            if csrf_inp and csrf_inp.get("value"):
                form_data[csrf_inp["name"]] = csrf_inp["value"]

            USER_F    = ["user", "email", "username", "login", "user_id", "phone", "mobile"]
            PASS_F    = ["pass", "password", "pwd", "passwd"]
            CAPT_F    = ["capt", "ans", "code", "result", "captcha", "verification"]

            for inp in inputs:
                name = inp.get("name")
                if not name:
                    continue
                nl = name.lower()
                if csrf_inp and name == csrf_inp.get("name"):
                    continue
                if any(f in nl for f in USER_F):
                    form_data[name] = self.username
                elif any(f in nl for f in PASS_F):
                    form_data[name] = self.password
                elif any(f in nl for f in CAPT_F):
                    form_data[name] = captcha_answer or inp.get("value", "")
                else:
                    form_data[name] = inp.get("value", "")

            if not any(any(f in k.lower() for f in USER_F) for k in form_data):
                form_data["username"] = self.username
            if not any(any(f in k.lower() for f in PASS_F) for k in form_data):
                form_data["password"] = self.password

            signin_candidates = list(dict.fromkeys(filter(None, [
                form_action_url,
                f"{base}/signin",
                f"{base}/login",
                login_url,
                f"{base}/auth/login",
            ])))

            OK_WORDS  = ["dashboard", "logout", "cdr", "smscdr", "inbox",
                         "/client/", "/agent/", "welcome", "sms report"]
            ERR_WORDS = ["invalid", "wrong", "error", "failed", "incorrect",
                         "unauthorized", "gagal", "salah"]

            await asyncio.sleep(0.8)

            for su in signin_candidates:
                try:
                    post = await client.post(
                        su, data=form_data,
                        headers={
                            "Referer":      login_url or su,
                            "Origin":       base,
                            "Content-Type": "application/x-www-form-urlencoded",
                        },
                        timeout=30,
                    )
                    fl        = str(post.url).lower()
                    bl        = post.text.lower()
                    not_login = not re.search(r"/(login|signin|sign-in)(/|$|\?)", fl)
                    has_ok    = any(w in bl for w in OK_WORDS)
                    still_pw  = bool(
                        BeautifulSoup(post.text, "html.parser")
                        .find("input", {"type": "password"})
                    )
                    has_error = any(w in bl for w in ERR_WORDS) and not has_ok

                    if has_error:
                        print(f"[S2/{self.tag}] Error response from {su} — trying next")
                        continue

                    if (not_login and not still_pw) or has_ok:
                        print(f"[S2/{self.tag}] ✅ Login OK via {su}")
                        self._role  = "agent" if "/agent" in fl else "client"
                        self._csrf  = _extract_csrf(post.text) or None
                        self._sesskey = None
                        self._skip_sesskey = False
                        if self._client:
                            await self._client.aclose()
                        self._client = client
                        return True
                except Exception:
                    continue

            print(f"[S2/{self.tag}] ❌ All login attempts failed (wrong credentials?)")
            await client.aclose()
            return False

        except Exception as e:
            print(f"[S2/{self.tag}] Login exception: {e}")
            try:
                await client.aclose()
            except Exception:
                pass
            return False

    async def _get_sesskey(self) -> str:
        if self._sesskey:
            return self._sesskey
        if self._skip_sesskey:
            return ""
        base  = self._base()
        roles = (["agent", "client"] if self._role == "agent" else ["client", "agent"])
        for role in roles:
            for path in (f"/{role}/SMSCDRStats", f"/{role}/dashboard", f"/{role}/"):
                try:
                    r = await self._client.get(f"{base}{path}", timeout=20)
                    if r.status_code != 200:
                        continue
                    if re.search(r"/(login|signin|sign-in|logon)(/|$|\?)",
                                 str(r.url).lower()):
                        continue
                    m = re.search(r"sesskey=([a-zA-Z0-9+/=]+)", r.text) or \
                        re.search(r"['\"]?sesskey['\"]?\s*[:=]\s*['\"]([^'\"]+)['\"]",
                                  r.text)
                    if m:
                        self._sesskey = m.group(1)
                        print(f"[S2/{self.tag}] sesskey: {self._sesskey[:10]}...")
                        return self._sesskey
                except Exception:
                    continue
        self._skip_sesskey = True
        return ""

    async def fetch_records(self) -> list | None:
        if not self._client:
            return None
        base    = self._base()
        sesskey = await self._get_sesskey()
        self._sesskey = None  # reset each cycle for freshness

        p = self.p

        # Try DataTables AJAX for both roles
        for role in ([self._role, "agent" if self._role == "client" else "client"]):
            ajax_url = _build_ajax_url(base, role)
            if sesskey:
                ajax_url += f"&sesskey={sesskey}"
            ref_url = f"{base}/{role}/SMSCDRStats"
            hdrs = {
                "X-Requested-With": "XMLHttpRequest",
                "Referer":          ref_url,
                "Accept":           "application/json, text/javascript, */*; q=0.01",
            }
            if self._csrf:
                hdrs["X-CSRF-TOKEN"] = self._csrf
            try:
                resp = await self._client.get(ajax_url, headers=hdrs, timeout=60)
                if resp.status_code in (401, 403, 502, 503, 504):
                    return None
                if _is_login_page(resp.text, str(resp.url)):
                    return None
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        if isinstance(data, dict) and ("aaData" in data or "data" in data):
                            recs = _parse_ajax_records(data, p)
                            if role != self._role:
                                print(f"[S2/{self.tag}] Role switch → {role}")
                                self._role = role
                            print(f"[S2/{self.tag}] AJAX [{role}] — {len(recs)} rows")
                            return recs
                    except Exception:
                        if _is_login_page(resp.text, str(resp.url)):
                            return None
            except httpx.ConnectError:
                return []
            except Exception as e:
                print(f"[S2/{self.tag}] AJAX error: {e}")

        # Fallback: fetch CDR HTML page and parse table
        msg_link = (p.get("msg_link") or "").strip()
        if not msg_link:
            msg_link = f"{base}/client/SMSCDRStats"
        if not msg_link.startswith("http"):
            msg_link = "http://" + msg_link
        try:
            r = await self._client.get(msg_link, timeout=30)
            if _is_login_page(r.text, str(r.url)):
                return None
            recs = _parse_html_records(r.text, p)
            print(f"[S2/{self.tag}] HTML fallback — {len(recs)} rows")
            return recs
        except Exception as e:
            print(f"[S2/{self.tag}] HTML fallback error: {e}")
            return []

    async def close(self):
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None


# ─── Worker per panel ─────────────────────────────────────────────────────────

async def _panel_worker(idx: int, p: dict):
    session    = _PanelSession(idx, p)
    tag        = session.tag
    fail_count = 0
    first_run  = True

    print(f"[S2/{tag}] Worker started | user={session.username}")

    while True:
        if not _get_settings:
            await asyncio.sleep(5)
            continue

        settings = _get_settings()
        panels   = settings.get("panels", [])
        if idx >= len(panels):
            print(f"[S2/{tag}] Panel removed — stopping worker")
            await session.close()
            return

        logged_in = await session.login()
        if not logged_in:
            fail_count += 1
            wait = min(60 * fail_count, 600)
            print(f"[S2/{tag}] Login failed (attempt {fail_count}) — retry in {wait}s")
            await asyncio.sleep(wait)
            continue

        fail_count = 0
        consec     = 0

        while True:
            # Verify panel still present
            settings = _get_settings()
            panels   = settings.get("panels", [])
            if idx >= len(panels):
                print(f"[S2/{tag}] Panel removed — closing worker")
                await session.close()
                return

            try:
                records = await session.fetch_records()

                if records is None:
                    print(f"[S2/{tag}] Session expired — re-login")
                    await session.close()
                    break

                if first_run:
                    # Mark all existing OTPs as seen so we don't re-forward them
                    count = 0
                    for rec in (records or []):
                        otp = _extract_otp(rec.get("message", ""))
                        if not otp:
                            continue
                        _mark_processed(_dedup_key(tag, rec["number"], otp))
                        count += 1
                    print(f"[S2/{tag}] Startup: {count} existing OTP(s) marked as seen")
                    first_run = False
                else:
                    new_count = 0
                    for rec in (records or []):
                        num = rec.get("number", "")
                        msg = rec.get("message", "")
                        if not num or not msg:
                            continue
                        otp = _extract_otp(msg)
                        if not otp:
                            continue
                        key = _dedup_key(tag, num, otp)
                        if _is_processed(key):
                            continue
                        _mark_processed(key)
                        # cli from scraped table (may be empty string if not detected)
                        rec_cli = rec.get("cli", "")
                        print(f"[S2/{tag}] 🔔 OTP {otp} | +{num} | CLI={rec_cli!r} | {msg[:50]!r}")
                        if _on_otp_found:
                            try:
                                _on_otp_found(num, otp, msg, tag, rec_cli)
                            except Exception as cb_err:
                                print(f"[S2/{tag}] Callback error: {cb_err}")
                        new_count += 1
                        await asyncio.sleep(0.05)
                    if new_count:
                        print(f"[S2/{tag}] ✅ {new_count} new OTP(s) forwarded")

                consec = 0

            except Exception as e:
                print(f"[S2/{tag}] Worker error: {e}")
                consec += 1
                if consec > 10:
                    print(f"[S2/{tag}] Too many consecutive errors — re-login")
                    await session.close()
                    break
                await asyncio.sleep(min(2 ** consec, 60))
                continue

            await asyncio.sleep(_FETCH_INTERVAL)

        await asyncio.sleep(5)


# ─── Supervisor: watches panels list, spawns/kills workers dynamically ────────

_worker_tasks: dict = {}

async def _supervisor():
    print("[S2] Supervisor started — watching bot_settings['panels']")
    while True:
        try:
            if _get_settings:
                panels = _get_settings().get("panels", [])
                for idx, p in enumerate(panels):
                    task = _worker_tasks.get(idx)
                    if task is None or task.done():
                        name = (p.get("name") or p.get("type") or f"Panel{idx}").strip()
                        print(f"[S2] Spawning worker for panel #{idx}: {name}")
                        t = asyncio.create_task(
                            _panel_worker(idx, p),
                            name=f"s2-worker-{idx}",
                        )
                        _worker_tasks[idx] = t

                # Cancel workers whose panels were removed
                for idx in list(_worker_tasks.keys()):
                    if idx >= len(panels):
                        task = _worker_tasks.pop(idx, None)
                        if task and not task.done():
                            task.cancel()
                            print(f"[S2] Cancelled worker for removed panel #{idx}")

        except Exception as e:
            print(f"[S2] Supervisor error: {e}")

        await asyncio.sleep(10)


# ─── Public API ───────────────────────────────────────────────────────────────

def start(on_otp_found, get_settings):
    """
    Start scraper2 in a background daemon thread.

    on_otp_found(num, otp, msg_text, panel_name) — called for each new OTP.
    get_settings()                                — returns live bot_settings dict.
    """
    global _on_otp_found, _get_settings, _loop

    _on_otp_found = on_otp_found
    _get_settings = get_settings

    def _run():
        global _loop
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
        try:
            _loop.run_until_complete(_supervisor())
        except Exception as e:
            print(f"[S2] Event loop crashed: {e}")
        finally:
            _loop.close()

    t = threading.Thread(target=_run, daemon=True, name="scraper2-loop")
    t.start()
    print("[S2] scraper2 background thread started ✅")
