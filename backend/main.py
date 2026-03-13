from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import secrets
import sqlite3
import smtplib
import ssl
import urllib.parse
from decimal import Decimal
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
from typing import Any

import boto3
import jwt
import requests
from botocore.exceptions import ClientError
from fastapi import FastAPI, Form, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from jwt import PyJWKClient
from pydantic import BaseModel, Field


TRANSFER_SELECTOR = "a9059cbb"
HEX_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}
APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISSUER = "https://appleid.apple.com"
DEFAULT_SESSION_DAYS = 30
DEFAULT_MAGIC_LINK_TTL_MINUTES = 20
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
APPLE_JWK_CLIENT = PyJWKClient(APPLE_JWKS_URL)
SES_IDENTITY_CLIENT = None


def utc_now() -> dt.datetime:
  return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def utc_now_iso() -> str:
  return utc_now().isoformat()


def parse_decimal(value: str, fallback: str) -> Decimal:
  try:
    return Decimal(value)
  except Exception:
    return Decimal(fallback)


def parse_bool_env(value: str | None, default: bool = False) -> bool:
  if value is None:
    return default
  return value.strip().lower() not in {"0", "false", "no", "off", ""}


def parse_iso_datetime(value: str | None) -> dt.datetime | None:
  if not value:
    return None
  try:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
  except ValueError:
    return None


APP_URL = os.getenv("APP_URL", "https://winspot24.com").strip().rstrip("/")
raw_allowed_origins = os.getenv("CORS_ORIGINS", "").strip()
ALLOWED_ORIGINS = [item.strip() for item in raw_allowed_origins.split(",") if item.strip()] if raw_allowed_origins else [
  APP_URL,
  "https://www.winspot24.com",
  "http://localhost:8080",
  "http://127.0.0.1:8080",
]

APP_ENV = {
  "app_url": APP_URL,
  "rpc_url": os.getenv("ETH_RPC_URL", "").strip(),
  "chain_id": int(os.getenv("CHAIN_ID", "1")),
  "usdt_contract": os.getenv("USDT_CONTRACT_ADDRESS", "0xdAC17F958D2ee523a2206206994597C13D831ec7").lower(),
  "treasury_address": os.getenv("TREASURY_ADDRESS", "0xC5AbC4ffE1d53d480dcadcdc4d2ccb66Fe96C47a").lower(),
  "total_tickets": int(os.getenv("TOTAL_TICKETS", "100")),
  "max_tickets_per_purchase": int(os.getenv("MAX_TICKETS_PER_PURCHASE", "20")),
  "ticket_price_usdt": parse_decimal(os.getenv("TICKET_PRICE_USDT", "10"), "10"),
  "sold_out_delay_blocks": int(os.getenv("SOLD_OUT_DELAY_BLOCKS", "5")),
  "shipping_start_date": os.getenv("SHIPPING_START_DATE", "2026-03-11"),
  "allowed_origins": ALLOWED_ORIGINS,
  "session_cookie_name": os.getenv("SESSION_COOKIE_NAME", "winspot24_session").strip() or "winspot24_session",
  "session_cookie_secure": parse_bool_env(os.getenv("SESSION_COOKIE_SECURE"), True),
  "session_days": int(os.getenv("SESSION_DAYS", str(DEFAULT_SESSION_DAYS))),
  "api_domain": os.getenv("API_DOMAIN", "api.winspot24.com").strip() or "api.winspot24.com",
  "smtp_host": os.getenv("SMTP_HOST", "").strip(),
  "smtp_port": int(os.getenv("SMTP_PORT", "587")),
  "smtp_username": os.getenv("SMTP_USERNAME", "").strip(),
  "smtp_password": os.getenv("SMTP_PASSWORD", ""),
  "smtp_sender_email": os.getenv("SMTP_SENDER_EMAIL", "").strip(),
  "smtp_sender_name": os.getenv("SMTP_SENDER_NAME", "Winspot24").strip() or "Winspot24",
  "smtp_starttls": parse_bool_env(os.getenv("SMTP_STARTTLS"), True),
  "smtp_use_ssl": parse_bool_env(os.getenv("SMTP_USE_SSL"), False),
  "magic_link_ttl_minutes": int(os.getenv("MAGIC_LINK_TTL_MINUTES", str(DEFAULT_MAGIC_LINK_TTL_MINUTES))),
  "email_auth_enabled_flag": parse_bool_env(os.getenv("EMAIL_AUTH_ENABLED"), False),
  "ses_region": os.getenv("SES_REGION", os.getenv("AWS_REGION", "eu-north-1")).strip() or "eu-north-1",
  "ses_identity_access_key_id": os.getenv("SES_IDENTITY_AWS_ACCESS_KEY_ID", "").strip(),
  "ses_identity_secret_access_key": os.getenv("SES_IDENTITY_AWS_SECRET_ACCESS_KEY", ""),
  "google_client_id": os.getenv("GOOGLE_CLIENT_ID", "").strip(),
  "apple_service_id": os.getenv("APPLE_SERVICE_ID", "").strip(),
  "apple_redirect_uri": os.getenv("APPLE_REDIRECT_URI", "https://api.winspot24.com/api/v1/auth/apple/callback").strip(),
}
APP_ENV["ticket_price_micro"] = int(APP_ENV["ticket_price_usdt"] * Decimal("1000000"))
APP_ENV["email_auth_enabled"] = bool(
  APP_ENV["email_auth_enabled_flag"] and APP_ENV["smtp_host"] and APP_ENV["smtp_sender_email"]
)
APP_ENV["google_auth_enabled"] = bool(APP_ENV["google_client_id"])
APP_ENV["apple_auth_enabled"] = bool(APP_ENV["apple_service_id"] and APP_ENV["apple_redirect_uri"])
APP_ENV["email_verification_enabled"] = bool(
  APP_ENV["ses_identity_access_key_id"] and APP_ENV["ses_identity_secret_access_key"]
)

if not HEX_ADDRESS_RE.match(APP_ENV["treasury_address"]):
  raise RuntimeError("Invalid TREASURY_ADDRESS")
if not HEX_ADDRESS_RE.match(APP_ENV["usdt_contract"]):
  raise RuntimeError("Invalid USDT_CONTRACT_ADDRESS")

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "winspot24.db"))

app = FastAPI(title="Winspot24 API", version="1.1.0")
app.add_middleware(
  CORSMiddleware,
  allow_origins=APP_ENV["allowed_origins"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


class ShippingPayload(BaseModel):
  full_name: str = Field(min_length=2, max_length=120)
  phone: str = Field(min_length=5, max_length=40)
  country: str = Field(min_length=2, max_length=80)
  city: str = Field(min_length=2, max_length=80)
  address_line1: str = Field(min_length=4, max_length=180)
  address_line2: str | None = Field(default=None, max_length=180)
  postal_code: str | None = Field(default=None, max_length=24)


class PurchasePayload(BaseModel):
  wallet_address: str
  tx_hash: str
  ticket_count: int = Field(ge=1, le=100)
  language: str | None = Field(default="en", max_length=12)
  shipping: ShippingPayload


class GoogleAuthPayload(BaseModel):
  credential: str = Field(min_length=20)


class EmailAuthRequestPayload(BaseModel):
  email: str = Field(min_length=5, max_length=320)
  return_to: str | None = Field(default=None, max_length=500)


class EmailVerificationRequestPayload(BaseModel):
  email: str = Field(min_length=5, max_length=320)


class AccountProfilePayload(BaseModel):
  full_name: str | None = Field(default=None, max_length=120)
  phone: str | None = Field(default=None, max_length=40)
  country: str | None = Field(default=None, max_length=80)
  city: str | None = Field(default=None, max_length=80)
  address_line1: str | None = Field(default=None, max_length=180)
  address_line2: str | None = Field(default=None, max_length=180)
  postal_code: str | None = Field(default=None, max_length=24)
  wallet_address: str | None = Field(default=None, max_length=42)


def get_conn() -> sqlite3.Connection:
  conn = sqlite3.connect(DB_PATH, isolation_level=None)
  conn.row_factory = sqlite3.Row
  conn.execute("PRAGMA foreign_keys = ON")
  conn.execute("PRAGMA journal_mode = WAL")
  return conn


def get_ses_identity_client():
  global SES_IDENTITY_CLIENT
  if SES_IDENTITY_CLIENT is None:
    if not APP_ENV["email_verification_enabled"]:
      raise HTTPException(status_code=503, detail="Email verification is not configured.")
    SES_IDENTITY_CLIENT = boto3.client(
      "sesv2",
      region_name=APP_ENV["ses_region"],
      aws_access_key_id=APP_ENV["ses_identity_access_key_id"],
      aws_secret_access_key=APP_ENV["ses_identity_secret_access_key"],
    )
  return SES_IDENTITY_CLIENT


def init_db() -> None:
  with get_conn() as conn:
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS rounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_number INTEGER NOT NULL UNIQUE,
        state TEXT NOT NULL,
        ticket_price_micro INTEGER NOT NULL,
        total_tickets INTEGER NOT NULL,
        sold_tickets INTEGER NOT NULL DEFAULT 0,
        draw_block_number INTEGER,
        winner_ticket_serial INTEGER,
        winner_wallet TEXT,
        created_at TEXT NOT NULL,
        sold_out_at TEXT,
        draw_completed_at TEXT
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_id INTEGER NOT NULL,
        wallet_address TEXT NOT NULL,
        tx_hash TEXT NOT NULL UNIQUE,
        ticket_count INTEGER NOT NULL,
        amount_micro INTEGER NOT NULL,
        language TEXT,
        shipping_full_name TEXT NOT NULL,
        shipping_phone TEXT NOT NULL,
        shipping_country TEXT NOT NULL,
        shipping_city TEXT NOT NULL,
        shipping_address_line1 TEXT NOT NULL,
        shipping_address_line2 TEXT,
        shipping_postal_code TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (round_id) REFERENCES rounds(id)
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_id INTEGER NOT NULL,
        serial INTEGER NOT NULL,
        wallet_address TEXT NOT NULL,
        purchase_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(round_id, serial),
        FOREIGN KEY (round_id) REFERENCES rounds(id),
        FOREIGN KEY (purchase_id) REFERENCES purchases(id)
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS shipping_updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_id INTEGER NOT NULL,
        step_order INTEGER NOT NULL,
        title TEXT NOT NULL,
        detail TEXT NOT NULL,
        planned_date TEXT NOT NULL,
        UNIQUE(round_id, step_order),
        FOREIGN KEY (round_id) REFERENCES rounds(id)
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT NOT NULL,
        provider_subject TEXT NOT NULL,
        email TEXT,
        email_verified INTEGER NOT NULL DEFAULT 0,
        full_name TEXT,
        avatar_url TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(provider, provider_subject)
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS user_profiles (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        phone TEXT,
        country TEXT,
        city TEXT,
        address_line1 TEXT,
        address_line2 TEXT,
        postal_code TEXT,
        wallet_address TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_token TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        last_seen_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS oauth_states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT NOT NULL,
        state TEXT NOT NULL UNIQUE,
        nonce TEXT,
        return_to TEXT,
        created_at TEXT NOT NULL
      )
      """
    )
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS magic_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        token_hash TEXT NOT NULL UNIQUE,
        return_to TEXT,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        used_at TEXT
      )
      """
    )


def normalize_address(value: str) -> str:
  raw = (value or "").strip().lower()
  if not HEX_ADDRESS_RE.match(raw):
    raise HTTPException(status_code=400, detail="Invalid wallet address.")
  return raw


def normalize_optional_address(value: str | None) -> str | None:
  raw = (value or "").strip()
  if not raw:
    return None
  return normalize_address(raw)


def normalize_hash(value: str) -> str:
  raw = (value or "").strip().lower()
  if not re.match(r"^0x[a-f0-9]{64}$", raw):
    raise HTTPException(status_code=400, detail="Invalid transaction hash.")
  return raw


def normalize_email(value: str) -> str:
  raw = (value or "").strip().lower()
  if not EMAIL_RE.match(raw):
    raise HTTPException(status_code=400, detail="Invalid email address.")
  return raw


def rpc_call(method: str, params: list[Any]) -> Any:
  if not APP_ENV["rpc_url"]:
    raise HTTPException(status_code=500, detail="ETH_RPC_URL is not configured on backend.")

  payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
  try:
    response = requests.post(APP_ENV["rpc_url"], json=payload, timeout=20)
    response.raise_for_status()
  except requests.RequestException as exc:
    raise HTTPException(status_code=502, detail=f"RPC request failed: {exc}") from exc

  body = response.json()
  if body.get("error"):
    raise HTTPException(status_code=502, detail=f"RPC error: {body['error']}")
  return body.get("result")


def eth_chain_id() -> int:
  value = rpc_call("eth_chainId", [])
  return int(value, 16)


def eth_block_number() -> int:
  value = rpc_call("eth_blockNumber", [])
  return int(value, 16)


def decode_erc20_transfer_input(input_data: str) -> tuple[str, int]:
  data = (input_data or "").lower().replace("0x", "")
  if len(data) < 8 + 64 + 64:
    raise HTTPException(status_code=400, detail="Invalid token transfer data.")
  if data[:8] != TRANSFER_SELECTOR:
    raise HTTPException(status_code=400, detail="Only direct USDT transfer is supported.")

  to_slot = data[8:72]
  amount_slot = data[72:136]
  to_address = "0x" + to_slot[-40:]
  amount = int(amount_slot, 16)
  return to_address.lower(), amount


def verify_payment_tx(tx_hash: str, wallet_address: str, expected_amount_micro: int) -> dict[str, Any]:
  if eth_chain_id() != APP_ENV["chain_id"]:
    raise HTTPException(status_code=400, detail="Wrong network. Switch wallet to Ethereum Mainnet.")

  tx = rpc_call("eth_getTransactionByHash", [tx_hash])
  if not tx:
    raise HTTPException(status_code=400, detail="Transaction not found.")

  receipt = rpc_call("eth_getTransactionReceipt", [tx_hash])
  if not receipt:
    raise HTTPException(status_code=400, detail="Transaction is not mined yet.")
  if int(receipt.get("status", "0x0"), 16) != 1:
    raise HTTPException(status_code=400, detail="Transaction failed on-chain.")

  tx_from = normalize_address(tx.get("from", ""))
  tx_to = normalize_address(tx.get("to", ""))
  if tx_from != wallet_address:
    raise HTTPException(status_code=400, detail="Transaction sender mismatch.")
  if tx_to != APP_ENV["usdt_contract"]:
    raise HTTPException(status_code=400, detail="Transaction is not sent to USDT contract.")

  destination, amount = decode_erc20_transfer_input(tx.get("input", ""))
  if destination != APP_ENV["treasury_address"]:
    raise HTTPException(status_code=400, detail="USDT destination mismatch.")
  if amount < expected_amount_micro:
    raise HTTPException(status_code=400, detail="USDT amount is lower than required for selected tickets.")

  return {
    "from": tx_from,
    "to": destination,
    "amount_micro": amount,
    "block_number": int(receipt["blockNumber"], 16),
  }


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
  return {key: row[key] for key in row.keys()}


def trim_optional_text(value: str | None) -> str | None:
  if value is None:
    return None
  trimmed = value.strip()
  return trimmed or None


def mask_email(value: str) -> str:
  local_part, domain_part = value.split("@", 1)
  if len(local_part) <= 2:
    masked_local = f"{local_part[:1]}***"
  else:
    masked_local = f"{local_part[:2]}***"
  return f"{masked_local}@{domain_part}"


def hash_magic_link_token(token: str) -> str:
  return hashlib.sha256(token.encode("utf-8")).hexdigest()


def append_query_value(url: str, key: str, value: str) -> str:
  parsed = urllib.parse.urlparse(url)
  query_items = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
  query_items.append((key, value))
  return urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(query_items)))


def empty_profile() -> dict[str, Any]:
  return {
    "full_name": None,
    "phone": None,
    "country": None,
    "city": None,
    "address_line1": None,
    "address_line2": None,
    "postal_code": None,
    "wallet_address": None,
  }


def serialize_profile_row(row: sqlite3.Row | None) -> dict[str, Any]:
  if not row:
    return empty_profile()
  return {
    "full_name": row["full_name"],
    "phone": row["phone"],
    "country": row["country"],
    "city": row["city"],
    "address_line1": row["address_line1"],
    "address_line2": row["address_line2"],
    "postal_code": row["postal_code"],
    "wallet_address": row["wallet_address"],
  }


def create_magic_link(conn: sqlite3.Connection, email: str, return_to: str) -> tuple[str, str]:
  cleanup_auth_tables(conn)
  token = secrets.token_urlsafe(32)
  token_hash = hash_magic_link_token(token)
  now = utc_now()
  expires_at = now + dt.timedelta(minutes=APP_ENV["magic_link_ttl_minutes"])
  conn.execute(
    """
    INSERT INTO magic_links (email, token_hash, return_to, created_at, expires_at, used_at)
    VALUES (?, ?, ?, ?, ?, NULL)
    """,
    (email, token_hash, sanitize_return_to(return_to), now.isoformat(), expires_at.isoformat()),
  )
  return token, token_hash


def consume_magic_link(conn: sqlite3.Connection, token: str) -> sqlite3.Row:
  cleanup_auth_tables(conn)
  row = conn.execute(
    """
    SELECT * FROM magic_links
    WHERE token_hash = ? AND used_at IS NULL
    LIMIT 1
    """,
    (hash_magic_link_token(token),),
  ).fetchone()
  if not row:
    raise HTTPException(status_code=400, detail="Magic link is invalid or expired.")

  expires_at = parse_iso_datetime(row["expires_at"])
  if not expires_at or expires_at <= utc_now():
    conn.execute("DELETE FROM magic_links WHERE id = ?", (row["id"],))
    raise HTTPException(status_code=400, detail="Magic link is invalid or expired.")

  conn.execute("UPDATE magic_links SET used_at = ? WHERE id = ?", (utc_now_iso(), row["id"]))
  return row


def send_magic_link_email(email: str, verify_url: str) -> None:
  if not APP_ENV["email_auth_enabled"]:
    raise HTTPException(status_code=503, detail="Email sign-in is not configured.")

  message = EmailMessage()
  message["Subject"] = "Your Winspot24 sign-in link"
  message["From"] = formataddr((APP_ENV["smtp_sender_name"], APP_ENV["smtp_sender_email"]))
  message["To"] = email

  ttl_minutes = APP_ENV["magic_link_ttl_minutes"]
  message.set_content(
    "Use this one-time sign-in link for your Winspot24 account.\n\n"
    f"{verify_url}\n\n"
    f"The link expires in {ttl_minutes} minutes."
  )
  message.add_alternative(
    "<p>Use this one-time sign-in link for your Winspot24 account.</p>"
    f"<p><a href=\"{verify_url}\">Open your account</a></p>"
    f"<p>This link expires in {ttl_minutes} minutes.</p>",
    subtype="html",
  )

  try:
    if APP_ENV["smtp_use_ssl"]:
      client: smtplib.SMTP | smtplib.SMTP_SSL = smtplib.SMTP_SSL(
        APP_ENV["smtp_host"],
        APP_ENV["smtp_port"],
        timeout=20,
        context=ssl.create_default_context(),
      )
    else:
      client = smtplib.SMTP(APP_ENV["smtp_host"], APP_ENV["smtp_port"], timeout=20)

    with client:
      if not APP_ENV["smtp_use_ssl"] and APP_ENV["smtp_starttls"]:
        client.starttls(context=ssl.create_default_context())
      if APP_ENV["smtp_username"]:
        client.login(APP_ENV["smtp_username"], APP_ENV["smtp_password"])
      client.send_message(message)
  except (smtplib.SMTPRecipientsRefused, smtplib.SMTPDataError) as exc:
    raw_message = str(exc)
    if "not verified" in raw_message.lower():
      raise HTTPException(
        status_code=409,
        detail=(
          "This email must be verified once before Winspot24 can send a sign-in link. "
          "Use the verification step first, then request the magic link again."
        ),
      ) from exc
    raise HTTPException(status_code=502, detail=f"Failed to send sign-in email: {raw_message}") from exc
  except Exception as exc:
    raise HTTPException(status_code=502, detail=f"Failed to send sign-in email: {exc}") from exc


def request_email_identity_verification(email: str) -> dict[str, str]:
  client = get_ses_identity_client()

  def get_status() -> str | None:
    try:
      response = client.get_email_identity(EmailIdentity=email)
      return response.get("VerificationStatus")
    except ClientError as exc:
      if exc.response.get("Error", {}).get("Code") in {"NotFoundException", "ResourceNotFoundException"}:
        return None
      raise

  current_status = get_status()
  if current_status == "SUCCESS":
    return {"status": "verified"}
  if current_status in {"PENDING", "TEMPORARY_FAILURE"}:
    try:
      client.delete_email_identity(EmailIdentity=email)
    except ClientError as exc:
      if exc.response.get("Error", {}).get("Code") not in {"NotFoundException", "ResourceNotFoundException"}:
        raise HTTPException(status_code=502, detail=f"Could not refresh email verification: {exc}") from exc

  try:
    client.create_email_identity(EmailIdentity=email)
  except ClientError as exc:
    if exc.response.get("Error", {}).get("Code") not in {"AlreadyExistsException"}:
      raise HTTPException(status_code=502, detail=f"Could not start email verification: {exc}") from exc

  refreshed_status = get_status()
  if refreshed_status == "SUCCESS":
    return {"status": "verified"}
  return {"status": "verification_sent"}


def sanitize_return_to(value: str | None) -> str:
  fallback = f"{APP_ENV['app_url']}/#account"
  raw = (value or "").strip()
  if not raw:
    return fallback

  parsed = urllib.parse.urlparse(raw)
  target_root = urllib.parse.urlparse(APP_ENV["app_url"])
  if not parsed.netloc:
    return urllib.parse.urljoin(f"{APP_ENV['app_url']}/", raw.lstrip("/"))
  if parsed.scheme == target_root.scheme and parsed.netloc == target_root.netloc:
    return raw
  return fallback


def cleanup_auth_tables(conn: sqlite3.Connection) -> None:
  now_iso = utc_now_iso()
  fifteen_minutes_ago = (utc_now() - dt.timedelta(minutes=15)).isoformat()
  conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (now_iso,))
  conn.execute("DELETE FROM oauth_states WHERE created_at <= ?", (fifteen_minutes_ago,))
  conn.execute("DELETE FROM magic_links WHERE expires_at <= ? OR used_at IS NOT NULL", (now_iso,))


def get_current_round(conn: sqlite3.Connection) -> sqlite3.Row | None:
  return conn.execute(
    "SELECT * FROM rounds WHERE state IN ('open', 'sold_out') ORDER BY round_number DESC LIMIT 1"
  ).fetchone()


def create_round(conn: sqlite3.Connection, round_number: int) -> sqlite3.Row:
  now = utc_now_iso()
  conn.execute(
    """
    INSERT INTO rounds (
      round_number, state, ticket_price_micro, total_tickets, sold_tickets, created_at
    ) VALUES (?, 'open', ?, ?, 0, ?)
    """,
    (round_number, APP_ENV["ticket_price_micro"], APP_ENV["total_tickets"], now),
  )
  return conn.execute("SELECT * FROM rounds WHERE round_number = ?", (round_number,)).fetchone()


def ensure_current_round(conn: sqlite3.Connection) -> sqlite3.Row:
  existing = get_current_round(conn)
  if existing:
    return existing

  max_round = conn.execute("SELECT COALESCE(MAX(round_number), 0) AS max_round FROM rounds").fetchone()[
    "max_round"
  ]
  return create_round(conn, max_round + 1)


def shipping_steps(start_date: dt.date) -> list[tuple[int, str, str, str]]:
  steps = [
    (1, "Готовим отправку", "Подготовка и упаковка приза на складе в Дубае.", 0),
    (2, "Передано перевозчику", "Передано международному перевозчику в Дубае.", 1),
    (3, "Международный транзит", "Посылка в международном транзите.", 3),
    (4, "Таможенное оформление", "Оформление на таможне страны получателя.", 6),
    (5, "Локальная доставка", "Передано локальной курьерской службе.", 8),
    (6, "Доставлено", "Приз доставлен победителю.", 9),
  ]
  return [
    (order, title, detail, (start_date + dt.timedelta(days=offset)).isoformat())
    for order, title, detail, offset in steps
  ]


def ensure_shipping_timeline(conn: sqlite3.Connection, round_id: int, drawn_at_iso: str) -> None:
  count = conn.execute(
    "SELECT COUNT(1) AS count FROM shipping_updates WHERE round_id = ?", (round_id,)
  ).fetchone()["count"]
  if count > 0:
    return

  requested_start = dt.date.fromisoformat(APP_ENV["shipping_start_date"])
  drawn_at = dt.datetime.fromisoformat(drawn_at_iso.replace("Z", "+00:00")).date()
  start_date = max(requested_start, drawn_at)

  for order, title, detail, planned_date in shipping_steps(start_date):
    conn.execute(
      """
      INSERT INTO shipping_updates (round_id, step_order, title, detail, planned_date)
      VALUES (?, ?, ?, ?, ?)
      """,
      (round_id, order, title, detail, planned_date),
    )


def maybe_finalize_round(conn: sqlite3.Connection) -> dict[str, Any] | None:
  sold_out = conn.execute(
    "SELECT * FROM rounds WHERE state = 'sold_out' ORDER BY round_number ASC LIMIT 1"
  ).fetchone()
  if not sold_out:
    return None

  draw_block = sold_out["draw_block_number"]
  if draw_block is None:
    return None

  current_block = eth_block_number()
  if current_block < draw_block:
    return {"status": "pending", "draw_block_number": draw_block, "blocks_left": draw_block - current_block}

  block = rpc_call("eth_getBlockByNumber", [hex(draw_block), False])
  if not block or not block.get("hash"):
    return {"status": "pending", "draw_block_number": draw_block, "blocks_left": 0}

  winner_serial = (int(block["hash"], 16) % sold_out["total_tickets"]) + 1
  ticket = conn.execute(
    "SELECT * FROM tickets WHERE round_id = ? AND serial = ?", (sold_out["id"], winner_serial)
  ).fetchone()
  if not ticket:
    raise HTTPException(status_code=500, detail="Winner ticket is missing.")

  now = utc_now_iso()
  conn.execute(
    """
    UPDATE rounds
    SET state = 'drawn',
        winner_ticket_serial = ?,
        winner_wallet = ?,
        draw_completed_at = ?
    WHERE id = ?
    """,
    (winner_serial, ticket["wallet_address"], now, sold_out["id"]),
  )
  ensure_shipping_timeline(conn, sold_out["id"], now)

  next_round_number = sold_out["round_number"] + 1
  exists_next = conn.execute(
    "SELECT id FROM rounds WHERE round_number = ?", (next_round_number,)
  ).fetchone()
  if not exists_next:
    create_round(conn, next_round_number)

  return {
    "status": "completed",
    "round_number": sold_out["round_number"],
    "winner_ticket_serial": winner_serial,
    "winner_wallet": ticket["wallet_address"],
    "draw_block_number": draw_block,
    "draw_block_hash": block["hash"],
  }


def round_payload(conn: sqlite3.Connection, row: sqlite3.Row, wallet: str | None = None) -> dict[str, Any]:
  sold = row["sold_tickets"]
  total = row["total_tickets"]
  remaining = max(total - sold, 0)
  base_payload = {
    "round_number": row["round_number"],
    "state": row["state"],
    "ticket_price_micro": row["ticket_price_micro"],
    "ticket_price_usdt": str(Decimal(row["ticket_price_micro"]) / Decimal("1000000")),
    "total_tickets": total,
    "sold_tickets": sold,
    "remaining_tickets": remaining,
    "draw_block_number": row["draw_block_number"],
    "winner_ticket_serial": row["winner_ticket_serial"],
    "winner_wallet": row["winner_wallet"],
    "created_at": row["created_at"],
    "sold_out_at": row["sold_out_at"],
    "draw_completed_at": row["draw_completed_at"],
  }
  if wallet:
    wallet_tickets = conn.execute(
      """
      SELECT serial, created_at
      FROM tickets
      WHERE round_id = ? AND wallet_address = ?
      ORDER BY serial DESC LIMIT 50
      """,
      (row["id"], wallet),
    ).fetchall()
    base_payload["wallet_tickets"] = [row_to_dict(item) for item in wallet_tickets]
  return base_payload


def timeline_payload(conn: sqlite3.Connection, round_number: int) -> dict[str, Any]:
  round_row = conn.execute("SELECT * FROM rounds WHERE round_number = ?", (round_number,)).fetchone()
  if not round_row:
    raise HTTPException(status_code=404, detail="Round not found.")

  rows = conn.execute(
    "SELECT * FROM shipping_updates WHERE round_id = ? ORDER BY step_order ASC", (round_row["id"],)
  ).fetchall()
  if not rows:
    return {"round_number": round_number, "items": [], "progress_percent": 0}

  today = dt.date.today()
  items: list[dict[str, Any]] = []
  completed = 0
  active_found = False

  for item in rows:
    planned_date = dt.date.fromisoformat(item["planned_date"])
    status = "pending"
    if planned_date < today:
      status = "completed"
      completed += 1
    elif planned_date == today and not active_found:
      status = "in_progress"
      active_found = True

    items.append(
      {
        "step_order": item["step_order"],
        "title": item["title"],
        "detail": item["detail"],
        "planned_date": item["planned_date"],
        "status": status,
      }
    )

  progress_percent = int((completed / len(rows)) * 100)
  return {"round_number": round_number, "items": items, "progress_percent": progress_percent}


def upsert_user(
  conn: sqlite3.Connection,
  *,
  provider: str,
  provider_subject: str,
  email: str | None,
  email_verified: bool,
  full_name: str | None,
  avatar_url: str | None,
) -> sqlite3.Row:
  existing = conn.execute(
    "SELECT * FROM users WHERE provider = ? AND provider_subject = ?",
    (provider, provider_subject),
  ).fetchone()
  now = utc_now_iso()
  clean_email = trim_optional_text(email)
  clean_name = trim_optional_text(full_name)
  clean_avatar = trim_optional_text(avatar_url)

  if existing:
    conn.execute(
      """
      UPDATE users
      SET email = ?,
          email_verified = ?,
          full_name = COALESCE(?, full_name),
          avatar_url = COALESCE(?, avatar_url),
          updated_at = ?
      WHERE id = ?
      """,
      (clean_email, 1 if email_verified else 0, clean_name, clean_avatar, now, existing["id"]),
    )
    return conn.execute("SELECT * FROM users WHERE id = ?", (existing["id"],)).fetchone()

  conn.execute(
    """
    INSERT INTO users (
      provider, provider_subject, email, email_verified, full_name, avatar_url, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (provider, provider_subject, clean_email, 1 if email_verified else 0, clean_name, clean_avatar, now, now),
  )
  user_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
  return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_profile_row(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
  return conn.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)).fetchone()


def save_profile(conn: sqlite3.Connection, user_id: int, payload: dict[str, Any]) -> sqlite3.Row:
  existing = get_profile_row(conn, user_id)
  current = serialize_profile_row(existing)
  merged = {**current, **payload}
  merged["wallet_address"] = normalize_optional_address(merged.get("wallet_address"))
  now = utc_now_iso()

  if existing:
    conn.execute(
      """
      UPDATE user_profiles
      SET full_name = ?,
          phone = ?,
          country = ?,
          city = ?,
          address_line1 = ?,
          address_line2 = ?,
          postal_code = ?,
          wallet_address = ?,
          updated_at = ?
      WHERE user_id = ?
      """,
      (
        trim_optional_text(merged.get("full_name")),
        trim_optional_text(merged.get("phone")),
        trim_optional_text(merged.get("country")),
        trim_optional_text(merged.get("city")),
        trim_optional_text(merged.get("address_line1")),
        trim_optional_text(merged.get("address_line2")),
        trim_optional_text(merged.get("postal_code")),
        merged.get("wallet_address"),
        now,
        user_id,
      ),
    )
  else:
    conn.execute(
      """
      INSERT INTO user_profiles (
        user_id, full_name, phone, country, city, address_line1, address_line2, postal_code, wallet_address, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      """,
      (
        user_id,
        trim_optional_text(merged.get("full_name")),
        trim_optional_text(merged.get("phone")),
        trim_optional_text(merged.get("country")),
        trim_optional_text(merged.get("city")),
        trim_optional_text(merged.get("address_line1")),
        trim_optional_text(merged.get("address_line2")),
        trim_optional_text(merged.get("postal_code")),
        merged.get("wallet_address"),
        now,
      ),
    )
  return conn.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)).fetchone()


def create_session(conn: sqlite3.Connection, user_id: int) -> str:
  cleanup_auth_tables(conn)
  now = utc_now()
  token = secrets.token_urlsafe(32)
  conn.execute(
    """
    INSERT INTO sessions (user_id, session_token, created_at, expires_at, last_seen_at)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
      user_id,
      token,
      now.isoformat(),
      (now + dt.timedelta(days=APP_ENV["session_days"])).isoformat(),
      now.isoformat(),
    ),
  )
  return token


def set_session_cookie(response: Response, token: str) -> None:
  response.set_cookie(
    key=APP_ENV["session_cookie_name"],
    value=token,
    max_age=APP_ENV["session_days"] * 24 * 60 * 60,
    expires=APP_ENV["session_days"] * 24 * 60 * 60,
    httponly=True,
    secure=APP_ENV["session_cookie_secure"],
    samesite="lax",
    path="/",
  )


def clear_session_cookie(response: Response) -> None:
  response.delete_cookie(
    key=APP_ENV["session_cookie_name"],
    path="/",
    httponly=True,
    secure=APP_ENV["session_cookie_secure"],
    samesite="lax",
  )


def session_bundle(conn: sqlite3.Connection, token: str | None) -> tuple[sqlite3.Row, sqlite3.Row | None] | None:
  cleanup_auth_tables(conn)
  if not token:
    return None

  session_row = conn.execute(
    "SELECT * FROM sessions WHERE session_token = ? LIMIT 1", (token,)
  ).fetchone()
  if not session_row:
    return None

  expires_at = parse_iso_datetime(session_row["expires_at"])
  if not expires_at or expires_at <= utc_now():
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_row["id"],))
    return None

  conn.execute("UPDATE sessions SET last_seen_at = ? WHERE id = ?", (utc_now_iso(), session_row["id"]))
  user_row = conn.execute("SELECT * FROM users WHERE id = ?", (session_row["user_id"],)).fetchone()
  if not user_row:
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_row["id"],))
    return None
  profile_row = get_profile_row(conn, user_row["id"])
  return user_row, profile_row


def require_session(conn: sqlite3.Connection, request: Request) -> tuple[sqlite3.Row, sqlite3.Row | None]:
  token = request.cookies.get(APP_ENV["session_cookie_name"])
  bundle = session_bundle(conn, token)
  if not bundle:
    raise HTTPException(status_code=401, detail="Sign in required.")
  return bundle


def session_payload(user_row: sqlite3.Row | None, profile_row: sqlite3.Row | None) -> dict[str, Any]:
  if not user_row:
    return {
      "authenticated": False,
      "user": None,
      "profile": empty_profile(),
    }

  return {
    "authenticated": True,
    "user": {
      "id": user_row["id"],
      "provider": user_row["provider"],
      "email": user_row["email"],
      "email_verified": bool(user_row["email_verified"]),
      "full_name": user_row["full_name"],
      "avatar_url": user_row["avatar_url"],
    },
    "profile": serialize_profile_row(profile_row),
  }


def parse_apple_user_payload(raw_user: str | None) -> dict[str, Any]:
  if not raw_user:
    return {}
  try:
    body = json.loads(raw_user)
  except json.JSONDecodeError:
    return {}

  name_info = body.get("name") or {}
  full_name = " ".join(part for part in [name_info.get("firstName"), name_info.get("lastName")] if part).strip() or None
  return {
    "email": trim_optional_text(body.get("email")),
    "full_name": full_name,
  }


def verify_google_credential(credential: str) -> dict[str, Any]:
  if not APP_ENV["google_auth_enabled"]:
    raise HTTPException(status_code=503, detail="Google sign-in is not configured.")

  try:
    payload = google_id_token.verify_oauth2_token(
      credential,
      google_requests.Request(),
      APP_ENV["google_client_id"],
    )
  except Exception as exc:
    raise HTTPException(status_code=400, detail=f"Google token verification failed: {exc}") from exc

  issuer = payload.get("iss")
  if issuer not in GOOGLE_ISSUERS:
    raise HTTPException(status_code=400, detail="Invalid Google issuer.")
  return payload


def verify_apple_identity_token(identity_token: str, expected_nonce: str | None = None) -> dict[str, Any]:
  if not APP_ENV["apple_auth_enabled"]:
    raise HTTPException(status_code=503, detail="Apple sign-in is not configured.")

  try:
    signing_key = APPLE_JWK_CLIENT.get_signing_key_from_jwt(identity_token)
    payload = jwt.decode(
      identity_token,
      signing_key.key,
      algorithms=["RS256"],
      audience=APP_ENV["apple_service_id"],
      issuer=APPLE_ISSUER,
    )
  except Exception as exc:
    raise HTTPException(status_code=400, detail=f"Apple token verification failed: {exc}") from exc

  if expected_nonce and payload.get("nonce") != expected_nonce:
    raise HTTPException(status_code=400, detail="Apple nonce mismatch.")
  return payload


def store_oauth_state(conn: sqlite3.Connection, provider: str, return_to: str) -> tuple[str, str]:
  cleanup_auth_tables(conn)
  state_value = secrets.token_urlsafe(24)
  nonce = secrets.token_urlsafe(24)
  conn.execute(
    "INSERT INTO oauth_states (provider, state, nonce, return_to, created_at) VALUES (?, ?, ?, ?, ?)",
    (provider, state_value, nonce, sanitize_return_to(return_to), utc_now_iso()),
  )
  return state_value, nonce


def consume_oauth_state(conn: sqlite3.Connection, provider: str, state_value: str) -> sqlite3.Row:
  row = conn.execute(
    "SELECT * FROM oauth_states WHERE provider = ? AND state = ? LIMIT 1", (provider, state_value)
  ).fetchone()
  if not row:
    raise HTTPException(status_code=400, detail="OAuth state is invalid or expired.")
  conn.execute("DELETE FROM oauth_states WHERE id = ?", (row["id"],))
  return row


def maybe_sync_profile_from_purchase(
  conn: sqlite3.Connection,
  request: Request,
  shipping: ShippingPayload,
  wallet_address: str,
) -> None:
  token = request.cookies.get(APP_ENV["session_cookie_name"])
  bundle = session_bundle(conn, token)
  if not bundle:
    return
  user_row, profile_row = bundle
  save_profile(
    conn,
    user_row["id"],
    {
      "full_name": shipping.full_name,
      "phone": shipping.phone,
      "country": shipping.country,
      "city": shipping.city,
      "address_line1": shipping.address_line1,
      "address_line2": shipping.address_line2,
      "postal_code": shipping.postal_code,
      "wallet_address": wallet_address,
    },
  )


@app.on_event("startup")
def on_startup() -> None:
  init_db()
  with get_conn() as conn:
    ensure_current_round(conn)
    cleanup_auth_tables(conn)


@app.get("/api/v1/health")
def health() -> dict[str, Any]:
  return {"ok": True, "time": utc_now_iso()}


@app.get("/api/v1/public/config")
def public_config() -> dict[str, Any]:
  return {
    "chain_id": APP_ENV["chain_id"],
    "chain_name": "Ethereum Mainnet",
    "token_symbol": "USDT",
    "token_standard": "ERC-20",
    "usdt_contract": APP_ENV["usdt_contract"],
    "treasury_address": APP_ENV["treasury_address"],
    "ticket_price_micro": APP_ENV["ticket_price_micro"],
    "ticket_price_usdt": str(APP_ENV["ticket_price_usdt"]),
    "total_tickets": APP_ENV["total_tickets"],
    "max_tickets_per_purchase": APP_ENV["max_tickets_per_purchase"],
    "shipping_start_date": APP_ENV["shipping_start_date"],
    "email_auth_enabled": APP_ENV["email_auth_enabled"],
    "email_verification_enabled": APP_ENV["email_verification_enabled"],
    "google_client_id": APP_ENV["google_client_id"] or None,
    "google_auth_enabled": APP_ENV["google_auth_enabled"],
    "apple_auth_enabled": APP_ENV["apple_auth_enabled"],
  }


@app.get("/api/v1/account/session")
def account_session(request: Request) -> dict[str, Any]:
  with get_conn() as conn:
    bundle = session_bundle(conn, request.cookies.get(APP_ENV["session_cookie_name"]))
    if not bundle:
      return session_payload(None, None)
    user_row, profile_row = bundle
    return session_payload(user_row, profile_row)


@app.put("/api/v1/account/profile")
def update_account_profile(payload: AccountProfilePayload, request: Request) -> dict[str, Any]:
  with get_conn() as conn:
    user_row, _ = require_session(conn, request)
    profile_row = save_profile(conn, user_row["id"], payload.model_dump())
    if trim_optional_text(payload.full_name):
      conn.execute(
        "UPDATE users SET full_name = ?, updated_at = ? WHERE id = ?",
        (trim_optional_text(payload.full_name), utc_now_iso(), user_row["id"]),
      )
      user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user_row["id"],)).fetchone()
    return session_payload(user_row, profile_row)


@app.post("/api/v1/auth/email/verification/request")
def request_email_verification(payload: EmailVerificationRequestPayload) -> dict[str, Any]:
  email = normalize_email(payload.email)
  result = request_email_identity_verification(email)
  return {
    "ok": True,
    "email": mask_email(email),
    "status": result["status"],
  }


@app.post("/api/v1/auth/email/request")
def request_email_sign_in(payload: EmailAuthRequestPayload, request: Request) -> dict[str, Any]:
  if not APP_ENV["email_auth_enabled"]:
    raise HTTPException(status_code=503, detail="Email sign-in is not configured.")

  email = normalize_email(payload.email)
  return_to = payload.return_to or f"{APP_ENV['app_url']}/#account"

  with get_conn() as conn:
    token, token_hash = create_magic_link(conn, email, return_to)
    verify_url = f"{str(request.base_url).rstrip('/')}/api/v1/auth/email/verify?token={urllib.parse.quote(token)}"
    try:
      send_magic_link_email(email, verify_url)
    except HTTPException:
      conn.execute("DELETE FROM magic_links WHERE token_hash = ?", (token_hash,))
      raise

  return {
    "ok": True,
    "email": mask_email(email),
    "ttl_minutes": APP_ENV["magic_link_ttl_minutes"],
  }


@app.get("/api/v1/auth/email/verify")
def verify_email_sign_in(token: str) -> Response:
  fallback_url = append_query_value(f"{APP_ENV['app_url']}/#account", "auth", "email-invalid")

  try:
    with get_conn() as conn:
      row = consume_magic_link(conn, token)
      user_row = upsert_user(
        conn,
        provider="email",
        provider_subject=row["email"],
        email=row["email"],
        email_verified=True,
        full_name=None,
        avatar_url=None,
      )
      profile_row = get_profile_row(conn, user_row["id"])
      session_token = create_session(conn, user_row["id"])
      target_url = append_query_value(sanitize_return_to(row["return_to"]), "auth", "email-verified")
      response = RedirectResponse(url=target_url, status_code=302)
      set_session_cookie(response, session_token)
      return response
  except HTTPException:
    return RedirectResponse(url=fallback_url, status_code=302)


@app.post("/api/v1/auth/google")
def google_sign_in(payload: GoogleAuthPayload) -> Response:
  claims = verify_google_credential(payload.credential)
  with get_conn() as conn:
    user_row = upsert_user(
      conn,
      provider="google",
      provider_subject=claims["sub"],
      email=claims.get("email"),
      email_verified=bool(claims.get("email_verified")),
      full_name=claims.get("name"),
      avatar_url=claims.get("picture"),
    )
    profile_row = get_profile_row(conn, user_row["id"])
    token = create_session(conn, user_row["id"])
    response = JSONResponse(session_payload(user_row, profile_row))
    set_session_cookie(response, token)
    return response


@app.get("/api/v1/auth/apple/start")
def apple_start(return_to: str | None = None) -> Response:
  if not APP_ENV["apple_auth_enabled"]:
    raise HTTPException(status_code=503, detail="Apple sign-in is not configured.")

  with get_conn() as conn:
    state_value, nonce = store_oauth_state(conn, "apple", return_to or f"{APP_ENV['app_url']}/#account")

  params = urllib.parse.urlencode(
    {
      "client_id": APP_ENV["apple_service_id"],
      "redirect_uri": APP_ENV["apple_redirect_uri"],
      "response_type": "code id_token",
      "response_mode": "form_post",
      "scope": "name email",
      "state": state_value,
      "nonce": nonce,
    }
  )
  return RedirectResponse(url=f"https://appleid.apple.com/auth/authorize?{params}", status_code=302)


@app.post("/api/v1/auth/apple/callback")
def apple_callback(
  state: str = Form(...),
  id_token: str = Form(...),
  user: str | None = Form(default=None),
) -> Response:
  with get_conn() as conn:
    state_row = consume_oauth_state(conn, "apple", state)
    claims = verify_apple_identity_token(id_token, state_row["nonce"])
    user_payload = parse_apple_user_payload(user)

    email_verified_raw = claims.get("email_verified")
    email_verified = email_verified_raw in {True, "true", "True", 1, "1"}
    email = user_payload.get("email") or claims.get("email")
    full_name = user_payload.get("full_name")

    user_row = upsert_user(
      conn,
      provider="apple",
      provider_subject=claims["sub"],
      email=email,
      email_verified=email_verified,
      full_name=full_name,
      avatar_url=None,
    )
    profile_row = get_profile_row(conn, user_row["id"])
    token = create_session(conn, user_row["id"])

    response = RedirectResponse(url=sanitize_return_to(state_row["return_to"]), status_code=302)
    set_session_cookie(response, token)
    return response


@app.post("/api/v1/auth/logout")
def logout(request: Request) -> Response:
  with get_conn() as conn:
    token = request.cookies.get(APP_ENV["session_cookie_name"])
    if token:
      conn.execute("DELETE FROM sessions WHERE session_token = ?", (token,))
  response = JSONResponse({"ok": True})
  clear_session_cookie(response)
  return response


@app.get("/api/v1/round/current")
def current_round(wallet: str | None = None) -> dict[str, Any]:
  normalized_wallet = normalize_address(wallet) if wallet else None
  with get_conn() as conn:
    maybe_finalize_round(conn)
    row = ensure_current_round(conn)
    return round_payload(conn, row, normalized_wallet)


@app.get("/api/v1/round/history")
def round_history(limit: int = 10) -> dict[str, Any]:
  limit = max(1, min(limit, 50))
  with get_conn() as conn:
    maybe_finalize_round(conn)
    rows = conn.execute(
      "SELECT * FROM rounds WHERE state = 'drawn' ORDER BY round_number DESC LIMIT ?",
      (limit,),
    ).fetchall()
    return {"items": [round_payload(conn, row) for row in rows]}


@app.get("/api/v1/round/{round_number}/shipping")
def shipping_timeline(round_number: int) -> dict[str, Any]:
  with get_conn() as conn:
    return timeline_payload(conn, round_number)


@app.post("/api/v1/round/finalize")
def finalize_round() -> dict[str, Any]:
  with get_conn() as conn:
    result = maybe_finalize_round(conn)
    if result is None:
      return {"status": "noop", "message": "No sold-out rounds pending finalization."}
    return result


@app.post("/api/v1/purchases")
def create_purchase(payload: PurchasePayload, request: Request) -> dict[str, Any]:
  wallet = normalize_address(payload.wallet_address)
  tx_hash = normalize_hash(payload.tx_hash)
  ticket_count = payload.ticket_count
  if ticket_count > APP_ENV["max_tickets_per_purchase"]:
    raise HTTPException(
      status_code=400,
      detail=f"Max {APP_ENV['max_tickets_per_purchase']} tickets per purchase.",
    )

  expected_amount_micro = ticket_count * APP_ENV["ticket_price_micro"]
  verify_payment_tx(tx_hash, wallet, expected_amount_micro)

  with get_conn() as conn:
    maybe_finalize_round(conn)
    current = ensure_current_round(conn)
    if current["state"] != "open":
      raise HTTPException(status_code=409, detail="Round is not open for purchase right now.")

    remaining = current["total_tickets"] - current["sold_tickets"]
    if ticket_count > remaining:
      raise HTTPException(status_code=400, detail=f"Only {remaining} tickets left in this round.")

    tx_used = conn.execute("SELECT id FROM purchases WHERE tx_hash = ?", (tx_hash,)).fetchone()
    if tx_used:
      raise HTTPException(status_code=409, detail="This transaction hash is already used.")

    now = utc_now_iso()
    conn.execute("BEGIN IMMEDIATE")
    try:
      conn.execute(
        """
        INSERT INTO purchases (
          round_id, wallet_address, tx_hash, ticket_count, amount_micro, language,
          shipping_full_name, shipping_phone, shipping_country, shipping_city,
          shipping_address_line1, shipping_address_line2, shipping_postal_code, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
          current["id"],
          wallet,
          tx_hash,
          ticket_count,
          expected_amount_micro,
          payload.language or "en",
          payload.shipping.full_name.strip(),
          payload.shipping.phone.strip(),
          payload.shipping.country.strip(),
          payload.shipping.city.strip(),
          payload.shipping.address_line1.strip(),
          (payload.shipping.address_line2 or "").strip() or None,
          (payload.shipping.postal_code or "").strip() or None,
          now,
        ),
      )
      purchase_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

      first_serial = current["sold_tickets"] + 1
      for serial in range(first_serial, first_serial + ticket_count):
        conn.execute(
          """
          INSERT INTO tickets (round_id, serial, wallet_address, purchase_id, created_at)
          VALUES (?, ?, ?, ?, ?)
          """,
          (current["id"], serial, wallet, purchase_id, now),
        )

      new_sold = current["sold_tickets"] + ticket_count
      new_state = "open"
      draw_block_number = None
      sold_out_at = None

      if new_sold >= current["total_tickets"]:
        new_sold = current["total_tickets"]
        new_state = "sold_out"
        sold_out_at = now
        draw_block_number = eth_block_number() + APP_ENV["sold_out_delay_blocks"]

      conn.execute(
        """
        UPDATE rounds
        SET sold_tickets = ?, state = ?, draw_block_number = ?, sold_out_at = ?
        WHERE id = ?
        """,
        (new_sold, new_state, draw_block_number, sold_out_at, current["id"]),
      )
      maybe_sync_profile_from_purchase(conn, request, payload.shipping, wallet)
      conn.execute("COMMIT")
    except Exception as exc:
      conn.execute("ROLLBACK")
      raise HTTPException(status_code=500, detail=f"Purchase failed: {exc}") from exc

    updated_round = conn.execute("SELECT * FROM rounds WHERE id = ?", (current["id"],)).fetchone()
    tickets = conn.execute(
      """
      SELECT serial
      FROM tickets
      WHERE round_id = ? AND purchase_id = ?
      ORDER BY serial ASC
      """,
      (current["id"], purchase_id),
    ).fetchall()

    return {
      "purchase_id": purchase_id,
      "tx_hash": tx_hash,
      "ticket_serials": [item["serial"] for item in tickets],
      "round": round_payload(conn, updated_round, wallet),
    }
