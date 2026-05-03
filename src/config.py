from __future__ import annotations

import os
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True), override=False)
load_dotenv(Path.cwd() / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    supabase_url: str | None
    supabase_key: str | None
    app_password: str | None
    supabase_key_source: str | None = None

    @property
    def has_supabase_credentials(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    @property
    def credential_signature(self) -> str:
        raw_value = f"{self.supabase_url or ''}:{self.supabase_key or ''}"
        return sha256(raw_value.encode("utf-8")).hexdigest()[:12]


def _clean_secret(value: Any) -> str | None:
    if value is None:
        return None

    cleaned = str(value).strip().strip('"').strip("'")
    return cleaned or None


def _streamlit_secret(name: str) -> str | None:
    try:
        import streamlit as st

        value: Any = st.secrets.get(name)
        return _clean_secret(value)
    except Exception:
        return None


def get_setting(name: str) -> str | None:
    return _streamlit_secret(name) or _clean_secret(os.getenv(name))


def get_first_setting(*names: str) -> tuple[str | None, str | None]:
    for name in names:
        value = get_setting(name)
        if value:
            return value, name
    return None, None


def get_settings() -> Settings:
    supabase_key, supabase_key_source = get_first_setting("SUPABASE_KEY", "SUPABASE_ANON_KEY")

    return Settings(
        supabase_url=get_setting("SUPABASE_URL"),
        supabase_key=supabase_key,
        app_password=get_setting("APP_PASSWORD"),
        supabase_key_source=supabase_key_source,
    )


def mask_secret(value: str | None) -> str:
    if not value:
        return "missing"
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def get_config_status() -> dict[str, str]:
    settings = get_settings()
    return {
        "SUPABASE_URL": "set" if settings.supabase_url else "missing",
        "SUPABASE_KEY": mask_secret(settings.supabase_key),
        "SUPABASE_KEY_SOURCE": settings.supabase_key_source or "missing",
        "APP_PASSWORD": "set" if settings.app_password else "missing",
    }


DEFAULT_CATEGORIES = [
    "Fresh Mango",
    "Gelato",
    "Sorbet",
    "Dessert",
    "Drink",
    "Savory Dish",
    "Other",
]


REVIEWERS = ["Reviewer 1", "Reviewer 2"]


CURRENCIES = ["EUR", "USD", "GBP", "THB", "INR", "JPY", "MXN", "BRL", "AUD", "CAD"]
