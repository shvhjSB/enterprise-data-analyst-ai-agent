"""Security primitives.

- API key auth middleware dependency
- Encryption utilities for storing DB connection configs
- PII policy utilities

Important: This repo stores encrypted config blobs on disk for demo/local use.
For enterprise deployments, swap this layer with Vault/KMS/HSM.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable

from cryptography.fernet import Fernet
from fastapi import Depends, Header, HTTPException, status

from text2sql_app.core.config import get_settings


def _derive_fernet_key(master_key: str) -> bytes:
    """Derive a Fernet key from a master secret.

    Accepts either base64/hex-ish strings; derives key via SHA-256.
    """
    digest = hashlib.sha256(master_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def get_fernet() -> Fernet:
    settings = get_settings()
    return Fernet(_derive_fernet_key(settings.text2sql_app_master_key))


def api_key_auth(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not x_api_key or not hmac.compare_digest(x_api_key, settings.text2sql_app_api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


@dataclass(frozen=True)
class EncryptedStore:
    """Encrypted JSON store on disk."""

    path: Path

    def load_all(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        token = self.path.read_bytes()
        if not token:
            return {}
        data = get_fernet().decrypt(token)
        return json.loads(data.decode("utf-8"))

    def save_all(self, obj: Dict[str, Any]) -> None:
        raw = json.dumps(obj).encode("utf-8")
        token = get_fernet().encrypt(raw)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(token)


PII_KEYWORDS_DEFAULT = {
    "email",
    "e_mail",
    "phone",
    "mobile",
    "ssn",
    "social_security",
    "dob",
    "date_of_birth",
    "address",
    "street",
    "zip",
    "postal",
    "passport",
    "national_id",
    "tax_id",
    "credit_card",
    "card_number",
}


def detect_pii_columns(column_names: Iterable[str]) -> set[str]:
    settings = get_settings()
    allow = {c.lower() for c in settings.pii_allowlist}
    deny = {c.lower() for c in settings.pii_denylist}

    pii = set()
    for col in column_names:
        c = col.lower()
        if c in allow:
            continue
        if c in deny:
            pii.add(col)
            continue
        if any(k in c for k in PII_KEYWORDS_DEFAULT):
            pii.add(col)
    return pii