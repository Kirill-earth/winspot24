from __future__ import annotations

import datetime as dt
import os
import re
import sqlite3
from decimal import Decimal
from pathlib import Path
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


TRANSFER_SELECTOR = "a9059cbb"
HEX_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")


def utc_now_iso() -> str:
  return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def parse_decimal(value: str, fallback: str) -> Decimal:
  try:
    return Decimal(value)
  except Exception:
    return Decimal(fallback)


APP_ENV = {
  "rpc_url": os.getenv("ETH_RPC_URL", "").strip(),
  "chain_id": int(os.getenv("CHAIN_ID", "1")),
  "usdt_contract": os.getenv("USDT_CONTRACT_ADDRESS", "0xdAC17F958D2ee523a2206206994597C13D831ec7").lower(),
  "treasury_address": os.getenv("TREASURY_ADDRESS", "0xC5AbC4ffE1d53d480dcadcdc4d2ccb66Fe96C47a").lower(),
  "total_tickets": int(os.getenv("TOTAL_TICKETS", "100")),
  "max_tickets_per_purchase": int(os.getenv("MAX_TICKETS_PER_PURCHASE", "20")),
  "ticket_price_usdt": parse_decimal(os.getenv("TICKET_PRICE_USDT", "10"), "10"),
  "sold_out_delay_blocks": int(os.getenv("SOLD_OUT_DELAY_BLOCKS", "5")),
  "shipping_start_date": os.getenv("SHIPPING_START_DATE", "2026-03-11"),
  "allowed_origins": [item.strip() for item in os.getenv("CORS_ORIGINS", "*").split(",") if item.strip()],
}
APP_ENV["ticket_price_micro"] = int(APP_ENV["ticket_price_usdt"] * Decimal("1000000"))

if not HEX_ADDRESS_RE.match(APP_ENV["treasury_address"]):
  raise RuntimeError("Invalid TREASURY_ADDRESS")
if not HEX_ADDRESS_RE.match(APP_ENV["usdt_contract"]):
  raise RuntimeError("Invalid USDT_CONTRACT_ADDRESS")

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = os.getenv("DB_PATH", str(DATA_DIR / "winspot24.db"))

app = FastAPI(title="Winspot24 API", version="1.0.0")
app.add_middleware(
  CORSMiddleware,
  allow_origins=APP_ENV["allowed_origins"] if APP_ENV["allowed_origins"] != ["*"] else ["*"],
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


def get_conn() -> sqlite3.Connection:
  conn = sqlite3.connect(DB_PATH, isolation_level=None)
  conn.row_factory = sqlite3.Row
  conn.execute("PRAGMA foreign_keys = ON")
  conn.execute("PRAGMA journal_mode = WAL")
  return conn


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


def normalize_address(value: str) -> str:
  raw = (value or "").strip().lower()
  if not HEX_ADDRESS_RE.match(raw):
    raise HTTPException(status_code=400, detail="Invalid wallet address.")
  return raw


def normalize_hash(value: str) -> str:
  raw = (value or "").strip().lower()
  if not re.match(r"^0x[a-f0-9]{64}$", raw):
    raise HTTPException(status_code=400, detail="Invalid transaction hash.")
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
  now = utc_now_iso()

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


@app.on_event("startup")
def on_startup() -> None:
  init_db()
  with get_conn() as conn:
    ensure_current_round(conn)


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
  }


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
def create_purchase(payload: PurchasePayload) -> dict[str, Any]:
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
