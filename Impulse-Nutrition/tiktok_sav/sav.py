#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31.0",
#   "python-dotenv>=1.0.0",
# ]
# ///
"""
TikTok SAV — Script d'ACK automatique (couche mécanique)

Rôle : liste les conversations TikTok Shop, envoie T0 ACK aux nouveaux messages
buyer, écrit les candidats dans pending.json pour traitement Claude (classification
intelligente + lookup BigBlue/Shopify).

Usage :
  python tiktok_sav/sav.py             # run normal
  python tiktok_sav/sav.py --dry-run   # simulation sans envoi ni écriture
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAV_DIR = Path(__file__).resolve().parent
STATE_PATH = SAV_DIR / "state.json"
PENDING_PATH = SAV_DIR / "pending.json"
LOG_PATH = SAV_DIR / "sav.log"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
logging.basicConfig(
    handlers=[_handler, logging.StreamHandler()],
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("tiktok_sav")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TIKTOK_MCP_ROOT = Path("/Users/antoinechabrat/Documents/SmallProject/Tiktok/MCP-TikTokShop")
load_dotenv(PROJECT_ROOT / ".env")          # credentials généraux
load_dotenv(TIKTOK_MCP_ROOT / ".env")       # credentials TikTok

APP_KEY = os.environ["TIKTOK_SHOP_APP_KEY"]
APP_SECRET = os.environ["TIKTOK_SHOP_APP_SECRET"]
ACCESS_TOKEN = os.environ["TIKTOK_SHOP_ACCESS_TOKEN"]
SHOP_CIPHER = os.environ.get("TIKTOK_SHOP_SHOP_CIPHER", "")

BASE_URL = "https://open-api.tiktokglobalshop.com"
API_VERSION = "202309"
DRY_RUN = "--dry-run" in sys.argv

# ---------------------------------------------------------------------------
# TikTok API — signing (porté depuis client.ts lignes 31-55)
# ---------------------------------------------------------------------------

def _sign(path: str, params: dict, body: dict | None = None) -> str:
    """HMAC-SHA256 : secret + path + sorted(params sans sign/token) + body_json + secret."""
    filtered = sorted(
        [(k, str(v)) for k, v in params.items() if k not in ("sign", "access_token")],
        key=lambda x: x[0],
    )
    param_str = "".join(f"{k}{v}" for k, v in filtered)
    body_str = json.dumps(body, separators=(",", ":"), ensure_ascii=False) if body else ""
    sign_str = APP_SECRET + path + param_str + body_str + APP_SECRET
    return hmac.new(APP_SECRET.encode(), sign_str.encode(), hashlib.sha256).hexdigest()


def _base_params() -> dict:
    p: dict = {"app_key": APP_KEY, "timestamp": str(int(time.time())), "access_token": ACCESS_TOKEN}
    if SHOP_CIPHER:
        p["shop_cipher"] = SHOP_CIPHER
    return p


def _request(method: str, path: str, params: dict | None = None, body: dict | None = None) -> Any:
    full_path = f"/{path}"
    qp = {**_base_params(), **(params or {})}
    qp["sign"] = _sign(full_path, qp, body)
    url = f"{BASE_URL}{full_path}?{urlencode(qp)}"
    headers = {"Content-Type": "application/json", "x-tts-access-token": ACCESS_TOKEN}
    resp = requests.request(method, url, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"TikTok API {data.get('code')}: {data.get('message')}")
    return data.get("data", {})

# ---------------------------------------------------------------------------
# TikTok API — helpers
# ---------------------------------------------------------------------------

def list_conversations(page_size: int = 20, max_pages: int = 5) -> list[dict]:
    """Fetch jusqu'à max_pages × page_size conversations en suivant next_page_token.

    Nécessaire parce que TikTok Shop pollue la liste avec des notifications ROBOT
    auto (delivery, order status) qui font remonter des convs sans activité buyer
    réelle, noyant les vrais messages acheteurs loin dans les pages suivantes.
    """
    all_convs: list[dict] = []
    page_token: str | None = None
    for _ in range(max_pages):
        params: dict = {"page_size": str(page_size)}
        if page_token:
            params["page_token"] = page_token
        data = _request("GET", f"customer_service/{API_VERSION}/conversations", params)
        all_convs.extend(data.get("conversations", []))
        page_token = data.get("next_page_token") or None
        if not page_token:
            break
    return all_convs


def read_conversation(conv_id: str, page_size: int = 5) -> list[dict]:
    data = _request(
        "GET",
        f"customer_service/{API_VERSION}/conversations/{conv_id}/messages",
        {"page_size": str(page_size)},
    )
    return data.get("messages", [])


def send_message(conv_id: str, text: str) -> None:
    """Envoie un message texte. Le content est double-wrappé (cf. conversations.ts:53-65)."""
    body = {"type": "TEXT", "content": json.dumps({"content": text})}
    _request("POST", f"customer_service/{API_VERSION}/conversations/{conv_id}/messages", {}, body)

# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def load_json(path: Path, default: Any) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            log.warning("JSON invalide : %s — réinitialisation", path.name)
    return default


def atomic_write(path: Path, data: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

T0_ACK = (
    "Bonjour,\n\n"
    "Merci pour votre message, nous revenons vers vous avec des solutions aussi rapidement que possible.\n\n"
    "Belle journée,\n"
    "Le service client"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_content(raw: str) -> str:
    """Parse le champ content TikTok (JSON-stringifié : {"content": "..."})."""
    try:
        return json.loads(raw).get("content", raw)
    except (json.JSONDecodeError, TypeError):
        return raw


def find_last_buyer_message(messages: list[dict]) -> dict | None:
    """Retourne le dernier message visible avec role == BUYER."""
    for msg in messages:
        if msg.get("sender", {}).get("role") == "BUYER" and msg.get("is_visible", True):
            return msg
    return None


def cs_replied_after(messages: list[dict], buyer_create_time: int) -> bool:
    """Retourne True si un CUSTOMER_SERVICE a répondu après le message buyer.

    Guard pour éviter de re-ACKer des convs déjà traitées manuellement ou
    par l'ancien skill (bootstrapping, ou run manuel entre deux crons).
    """
    for msg in messages:
        if (
            msg.get("sender", {}).get("role") == "CUSTOMER_SERVICE"
            and msg.get("create_time", 0) > buyer_create_time
            and msg.get("is_visible", True)
        ):
            return True
    return False

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run() -> None:
    log.info("=== TikTok SAV sav.py — %s===", "[DRY RUN] " if DRY_RUN else "")

    state: dict = load_json(STATE_PATH, {})
    pending: list = load_json(PENDING_PATH, [])
    pending_ids = {e["conv_id"] for e in pending}

    # 1. Fetch conversations
    try:
        conversations = list_conversations(page_size=20)
    except Exception as exc:
        log.error("Erreur list_conversations : %s", exc)
        return

    n_ack = n_skip = n_pending = 0

    for conv in conversations:
        conv_id: str = conv["id"]
        unread: int = conv.get("unread_count", 0)
        buyer = next((p for p in conv.get("participants", []) if p["role"] == "BUYER"), {})
        buyer_username: str = buyer.get("nickname", conv_id)
        last_acked_id: str = state.get(conv_id, {}).get("last_acked_message_id", "")

        # Le bot TikTok remplace latest_message.sender par ROBOT/SYSTEM (greeting
        # auto ou placeholder [Other] pour les médias) et reset unread_count=0.
        # On lit donc le thread à chaque run pour retrouver le dernier BUYER réel.
        try:
            context_messages = read_conversation(conv_id, page_size=10)
        except Exception as exc:
            log.warning("Erreur read_conversation %s : %s — skip", buyer_username, exc)
            n_skip += 1
            continue

        buyer_msg_obj = find_last_buyer_message(context_messages)
        if buyer_msg_obj is None:
            log.debug("SKIP (aucun BUYER dans la conv) : %s", buyer_username)
            n_skip += 1
            continue

        buyer_msg_id = buyer_msg_obj["id"]
        if buyer_msg_id == last_acked_id:
            log.debug("SKIP (déjà acked) : %s", buyer_username)
            n_skip += 1
            continue

        if cs_replied_after(context_messages, buyer_msg_obj.get("create_time", 0)):
            log.debug("SKIP (CS a déjà répondu) : %s", buyer_username)
            n_skip += 1
            continue

        buyer_msg = parse_content(buyer_msg_obj.get("content", "{}"))

        # --- Candidat détecté ---
        log.info("CANDIDAT : %-25s | %.60s", buyer_username, buyer_msg)

        # Envoyer T0 ACK
        if DRY_RUN:
            log.info("[DRY RUN] T0 ACK → %s", buyer_username)
            n_ack += 1
        else:
            try:
                send_message(conv_id, T0_ACK)
                log.info("T0 ACK envoyé → %s", buyer_username)
                n_ack += 1
            except Exception as exc:
                log.error("Erreur T0 ACK → %s : %s — skip", buyer_username, exc)
                n_skip += 1
                continue

        # Mettre à jour state
        state[conv_id] = {
            "last_acked_message_id": buyer_msg_id,
            "last_replied_at": int(time.time()),
            "last_category": "T0_ACK",
        }

        # Append à pending (dedup par conv_id)
        if conv_id not in pending_ids:
            pending.append({
                "conv_id": conv_id,
                "buyer_username": buyer_username,
                "buyer_message": buyer_msg,
                "buyer_message_id": buyer_msg_id,
                "context_messages": context_messages,
                "unread_count": unread,
                "queued_at": datetime.now(timezone.utc).isoformat(),
            })
            pending_ids.add(conv_id)
            n_pending += 1
            log.info("→ pending.json : %s", buyer_username)

    # Écriture atomique (pas en dry-run)
    if not DRY_RUN:
        atomic_write(STATE_PATH, state)
        atomic_write(PENDING_PATH, pending)
        log.info("state.json + pending.json écrits")

    log.info(
        "=== Terminé : %d ACK envoyés | %d en pending pour Claude | %d skippés ===",
        n_ack, n_pending, n_skip,
    )


if __name__ == "__main__":
    run()
