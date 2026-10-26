from __future__ import annotations

import json
import os
import sqlite3
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = os.getenv("DATABASE_PATH", "creatorflow.db")
AI_API_BASE_URL = os.getenv("AI_API_BASE_URL", "").rstrip("/")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "")
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")],
    }
}

app = FastAPI(title="CreatorFlow", description="Policy-aware YouTube channel operations")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "development-only-change-me"),
    https_only=os.getenv("APP_ENV") == "production",
    same_site="lax",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def connect_db() -> sqlite3.Connection:
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db() -> None:
    with connect_db() as db:
        db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        db.execute("""CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, audience TEXT NOT NULL DEFAULT '',
            viewer_value TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Idea',
            target_date TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS content_packs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT NOT NULL, format TEXT NOT NULL,
            audience TEXT NOT NULL, duration TEXT NOT NULL, body TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")


@app.on_event("startup")
def startup() -> None:
    init_db()


def get_setting(key: str) -> str | None:
    with connect_db() as db:
        row = db.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None


def save_setting(key: str, value: str) -> None:
    with connect_db() as db:
        db.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))


def load_credentials() -> Credentials | None:
    raw = get_setting("google_credentials")
    if not raw:
        return None
    try:
        info = json.loads(raw)
        creds = Credentials.from_authorized_user_info(info, SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
            save_setting("google_credentials", creds.to_json())
        return creds if creds.valid else None
    except Exception:
        return None


def demo_data() -> dict[str, Any]:
    return {
        "connected": False,
        "channel": {"title": "Your channel", "description": "Connect YouTube to load your channel."},
        "totals": {"views": 18420, "minutes": 92500, "subs": 312, "avg_view": 301},
        "series": [
            {"day": (date.today() - timedelta(days=6-i)).strftime("%b %d"), "views": v}
            for i, v in enumerate([2100, 2380, 2250, 2810, 2680, 3020, 3180])
        ],
        "top_video": "Demo: Replace this with your own original video",
    }


def youtube_data(creds: Credentials) -> dict[str, Any]:
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
    result = youtube.channels().list(part="snippet,statistics", mine=True).execute()
    items = result.get("items", [])
    if not items:
        raise RuntimeError("No YouTube channel was found for this Google account.")
    channel = items[0]
    analytics = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=27)
    report = analytics.reports().query(
        ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(),
        metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost",
        dimensions="day", sort="day",
    ).execute()
    rows = report.get("rows", [])
    totals = {
        "views": sum(int(row[1]) for row in rows),
        "minutes": sum(int(row[2]) for row in rows),
        "avg_view": round(sum(float(row[3]) for row in rows) / max(len(rows), 1)),
        "subs": sum(int(row[4]) - int(row[5]) for row in rows),
    }
    series = [{"day": row[0][5:], "views": int(row[1])} for row in rows[-7:]]
    return {
        "connected": True,
        "channel": {"title": channel["snippet"]["title"], "description": channel["snippet"].get("description", "")},
        "totals": totals,
        "series": series,
        "top_video": "Use YouTube Studio to inspect top videos and traffic sources.",
    }


def get_ideas() -> list[dict[str, Any]]:
    with connect_db() as db:
        rows = db.execute("SELECT * FROM ideas ORDER BY CASE WHEN target_date='' THEN 1 ELSE 0 END, target_date, id DESC").fetchall()
        return [dict(row) for row in rows]


def get_content_packs() -> list[dict[str, Any]]:
    with connect_db() as db:
        return [dict(row) for row in db.execute("SELECT id,topic,format,audience,duration,created_at FROM content_packs ORDER BY id DESC LIMIT 12")]


def generate_content_pack(topic: str, audience: str, viewer_value: str, video_format: str, duration: str) -> str:
    if not (AI_API_BASE_URL and AI_API_KEY and AI_MODEL):
        raise RuntimeError("Configure AI_API_BASE_URL, AI_API_KEY, and AI_MODEL in .env to generate content.")
    prompt = f"""Create an original YouTube production pack for a creator. The topic is an input, not permission to copy another creator or source. Make the video specific, useful, and clearly distinct; avoid generic filler, repeated templates, fake engagement, unsupported claims, fabricated quotations, and promises of views, subscribers, or revenue. If the topic needs facts, mark claims that require checking and include suggested authoritative source types/links to verify; do not invent citations. Never imitate a named creator or living person's voice/style.

Topic: {topic}
Intended audience: {audience or 'general viewers who are genuinely interested in this topic'}
Viewer value / creator's original angle: {viewer_value or 'Propose a distinct, useful angle and label assumptions the creator must personalize.'}
Format: {video_format}
Target runtime: {duration}

Return a complete, production-ready Markdown pack with these sections:
1. Creative brief (promise, original angle, assumptions to personalize)
2. Three honest title options (accurate, no misleading clickbait)
3. Thumbnail concept and a text-to-image prompt using original, non-infringing elements
4. Full spoken script with a compelling but truthful opening, clear sections, transitions, and a useful ending; pace it to the runtime and include approximate timestamps
5. Scene-by-scene storyboard (time, visuals/B-roll to create or license, on-screen text, narration)
6. Description, a small relevant tag list, and chapters that match the script
7. Shorts cut-down: a distinct 30-60 second excerpt with hook, payoff, and caption
8. Pre-publish checklist: factual verification, rights, disclosures (including synthetic/altered media if applicable), accessibility, title accuracy, and human review

Write for this one topic and audience, not as interchangeable mass-produced content. Do not claim the pack itself guarantees policy compliance or growth."""
    payload = json.dumps({
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": "You are a careful, original YouTube producer. Create useful production material and distinguish verifiable facts from creative framing."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }).encode("utf-8")
    req = urllib.request.Request(
        AI_API_BASE_URL + "/chat/completions", data=payload,
        headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
        body = result["choices"][0]["message"]["content"]
        if not isinstance(body, str) or not body.strip():
            raise RuntimeError("The AI provider returned an empty content pack.")
        return body.strip()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"AI provider returned HTTP {exc.code}. Check the provider URL, model, and API key.") from None
    except urllib.error.URLError:
        raise RuntimeError("Could not reach the AI provider. Check the endpoint and network connection.") from None
    except (KeyError, IndexError, json.JSONDecodeError):
        raise RuntimeError("The AI provider response was not in the expected chat completions format.") from None


def recommendations(data: dict[str, Any]) -> list[dict[str, str]]:
    views = data["totals"]["views"]
    mins = data["totals"]["minutes"]
    avg = data["totals"]["avg_view"]
    subs = data["totals"]["subs"]
    out = []
    if views:
        out.append({"title": "Study the opening 30 seconds", "body": f"Your recent average view duration is {avg // 60}m {avg % 60}s. Compare the first 30 seconds of your top and lowest-retention videos, then test one clearer opening in a new original video."})
        out.append({"title": "Turn a viewer question into a useful follow-up", "body": "Review comments in YouTube Studio, identify a genuine unanswered question, and plan a distinct video that fully answers it. Avoid repetitive reply or comment campaigns."})
        out.append({"title": "Build a repeatable learning loop", "body": f"You gained {subs:+,} net subscribers across {views:,} views in this period. Compare topics and viewer value across videos; use the pattern as a hypothesis, not a promise."})
    else:
        out.append({"title": "Start with one audience promise", "body": "Write down who your channel helps and what each video will help them do. Make one original pilot with a clear beginning, useful middle, and satisfying finish."})
    if mins == 0:
        out.append({"title": "Reconnect analytics", "body": "Analytics data may take time to appear or may be unavailable for a new channel. Check YouTube Studio and reconnect the Google account with channel access."})
    return out[:3]


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    creds = load_credentials()
    error = request.session.pop("oauth_error", None)
    data = demo_data()
    if creds:
        try:
            data = youtube_data(creds)
        except Exception as exc:
            error = f"YouTube data could not be loaded: {str(exc)[:180]}"
    ideas = get_ideas()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "data": data, "ideas": ideas,
        "recommendations": recommendations(data), "error": error,
        "configured": bool(CLIENT_CONFIG["web"]["client_id"] and CLIENT_CONFIG["web"]["client_secret"]),
    })


@app.get("/studio", response_class=HTMLResponse)
def studio(request: Request):
    return templates.TemplateResponse("studio.html", {
        "request": request, "packs": get_content_packs(), "result": None,
        "error": request.session.pop("studio_error", None),
        "configured": bool(AI_API_BASE_URL and AI_API_KEY and AI_MODEL),
    })


@app.post("/studio/generate", response_class=HTMLResponse)
def studio_generate(request: Request, topic: str = Form(...), audience: str = Form(""), viewer_value: str = Form(""), video_format: str = Form("Long-form video"), duration: str = Form("6-8 minutes")):
    topic = topic.strip()[:300]
    audience = audience.strip()[:240]
    viewer_value = viewer_value.strip()[:500]
    if not topic:
        error = "Add a topic to generate a production pack."
        return templates.TemplateResponse("studio.html", {"request": request, "packs": get_content_packs(), "result": None, "error": error, "configured": bool(AI_API_BASE_URL and AI_API_KEY and AI_MODEL)})
    try:
        body = generate_content_pack(topic, audience, viewer_value, video_format[:40], duration[:40])
        with connect_db() as db:
            cursor = db.execute("INSERT INTO content_packs(topic,format,audience,duration,body) VALUES(?,?,?,?,?)", (topic, video_format[:40], audience, duration[:40], body))
            pack_id = cursor.lastrowid
        result = {"id": pack_id, "topic": topic, "format": video_format, "audience": audience, "duration": duration, "body": body}
        return templates.TemplateResponse("studio.html", {"request": request, "packs": get_content_packs(), "result": result, "error": None, "configured": True})
    except RuntimeError as exc:
        return templates.TemplateResponse("studio.html", {"request": request, "packs": get_content_packs(), "result": None, "error": str(exc), "configured": bool(AI_API_BASE_URL and AI_API_KEY and AI_MODEL)})


@app.get("/studio/{pack_id}/download")
def download_content_pack(pack_id: int):
    from fastapi.responses import Response
    with connect_db() as db:
        pack = db.execute("SELECT * FROM content_packs WHERE id=?", (pack_id,)).fetchone()
    if not pack:
        return RedirectResponse("/studio", status_code=303)
    filename = f"creatorflow-pack-{pack_id}.md"
    return Response(pack["body"], media_type="text/markdown; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@app.get("/auth/start")
def auth_start(request: Request):
    if not CLIENT_CONFIG["web"]["client_id"] or not CLIENT_CONFIG["web"]["client_secret"]:
        request.session["oauth_error"] = "Add Google OAuth credentials to .env before connecting."
        return RedirectResponse("/", status_code=303)
    flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, redirect_uri=CLIENT_CONFIG["web"]["redirect_uris"][0])
    url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent")
    request.session["oauth_state"] = state
    return RedirectResponse(url, status_code=302)


@app.get("/auth/callback")
def auth_callback(request: Request, state: str = "", code: str = "", error: str = ""):
    expected = request.session.pop("oauth_state", None)
    if error or not expected or state != expected:
        request.session["oauth_error"] = "Google sign-in was cancelled or its security state did not match. Please try again."
        return RedirectResponse("/", status_code=303)
    try:
        flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, state=state, redirect_uri=CLIENT_CONFIG["web"]["redirect_uris"][0])
        flow.fetch_token(code=code)
        save_setting("google_credentials", flow.credentials.to_json())
    except Exception:
        request.session["oauth_error"] = "Google sign-in could not be completed. Check OAuth setup and try again."
    return RedirectResponse("/", status_code=303)


@app.post("/auth/disconnect")
def disconnect():
    with connect_db() as db:
        db.execute("DELETE FROM settings WHERE key='google_credentials'")
    return RedirectResponse("/", status_code=303)


@app.post("/ideas")
def add_idea(title: str = Form(...), audience: str = Form(""), viewer_value: str = Form(""), target_date: str = Form("")):
    clean_title = title.strip()[:160]
    if clean_title:
        with connect_db() as db:
            db.execute("INSERT INTO ideas(title,audience,viewer_value,target_date) VALUES(?,?,?,?)", (clean_title, audience.strip()[:240], viewer_value.strip()[:500], target_date[:10]))
    return RedirectResponse("/#planner", status_code=303)


@app.post("/ideas/{idea_id}/status")
def update_idea_status(idea_id: int, status: str = Form(...)):
    allowed = {"Idea", "Draft", "Review", "Published"}
    if status in allowed:
        with connect_db() as db:
            db.execute("UPDATE ideas SET status=? WHERE id=?", (status, idea_id))
    return RedirectResponse("/#planner", status_code=303)


@app.get("/health")
def health():
    return {"status": "ok", "app": "CreatorFlow"}
