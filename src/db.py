from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st
from supabase import Client, create_client

from src.config import get_config_status, get_settings
from src.scoring import calculate_final_score


REVIEW_COLUMNS = [
    "id",
    "created_at",
    "name",
    "category",
    "country",
    "city",
    "place_name",
    "latitude",
    "longitude",
    "date_tasted",
    "reviewer",
    "price",
    "currency",
    "sweetness",
    "acidity",
    "aroma",
    "texture",
    "mango_intensity",
    "value_for_money",
    "final_score",
    "short_review",
    "image_url",
    "would_eat_again",
    "public",
]

STORAGE_BUCKET = "review-images"
LOCAL_UPLOAD_DIR = Path("uploads")


@st.cache_resource(show_spinner=False)
def _create_supabase_client(supabase_url: str, supabase_key: str) -> Client | None:
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as exc:
        st.error(f"Could not create Supabase client: {exc}")
        return None


def get_supabase_client() -> Client | None:
    settings = get_settings()
    if not settings.has_supabase_credentials:
        return None

    return _create_supabase_client(settings.supabase_url, settings.supabase_key)


@st.cache_data(ttl=60, show_spinner=False)
def _load_reviews_cached(credential_signature: str) -> tuple[pd.DataFrame, str | None]:
    _ = credential_signature
    client = get_supabase_client()
    if client is None:
        return pd.DataFrame(columns=REVIEW_COLUMNS), (
            "Supabase client could not be created even though credentials were found."
        )

    try:
        response = (
            client.table("reviews")
            .select("*")
            .eq("public", True)
            .order("final_score", desc=True)
            .execute()
        )
    except Exception as exc:
        return pd.DataFrame(columns=REVIEW_COLUMNS), f"Could not load reviews: {exc}"

    records = response.data or []
    if not records:
        return pd.DataFrame(columns=REVIEW_COLUMNS), None

    df = pd.DataFrame(records)
    for column in REVIEW_COLUMNS:
        if column not in df.columns:
            df[column] = None

    numeric_columns = [
        "latitude",
        "longitude",
        "price",
        "sweetness",
        "acidity",
        "aroma",
        "texture",
        "mango_intensity",
        "value_for_money",
        "final_score",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df[REVIEW_COLUMNS], None


def load_reviews() -> tuple[pd.DataFrame, str | None]:
    settings = get_settings()
    if not settings.has_supabase_credentials:
        status = get_config_status()
        return pd.DataFrame(columns=REVIEW_COLUMNS), (
            "Supabase is not configured yet. Add SUPABASE_URL and SUPABASE_KEY or "
            "SUPABASE_ANON_KEY to .env locally or Streamlit secrets in deployment. "
            f"Current config: URL {status['SUPABASE_URL']}, key {status['SUPABASE_KEY']} "
            f"from {status['SUPABASE_KEY_SOURCE']}."
        )

    return _load_reviews_cached(settings.credential_signature)


def insert_review(payload: dict[str, Any]) -> tuple[bool, str]:
    client = get_supabase_client()
    if client is None:
        return False, "Supabase credentials are missing."

    if payload.get("final_score") in (None, ""):
        payload["final_score"] = calculate_final_score(payload)

    cleaned_payload = {
        key: value
        for key, value in payload.items()
        if key in REVIEW_COLUMNS and key not in {"id", "created_at"} and value not in ("", None)
    }

    try:
        client.table("reviews").insert(cleaned_payload).execute()
        _load_reviews_cached.clear()
        return True, "Review added."
    except Exception as exc:
        return False, f"Could not add review: {exc}"


def _safe_upload_name(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"

    stem = Path(filename).stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "-", stem).strip("-") or "review-image"
    return f"{stem}-{uuid4().hex[:12]}{suffix}"


def _content_type(filename: str, fallback: str | None = None) -> str:
    if fallback:
        return fallback

    suffix = Path(filename).suffix.lower()
    if suffix == ".png":
        return "image/png"
    if suffix == ".webp":
        return "image/webp"
    return "image/jpeg"


def _save_uploaded_image_locally(file_name: str, data: bytes) -> tuple[bool, str, str]:
    LOCAL_UPLOAD_DIR.mkdir(exist_ok=True)
    local_path = LOCAL_UPLOAD_DIR / file_name
    local_path.write_bytes(data)
    return True, str(local_path).replace("\\", "/"), (
        "Image saved locally for development. Configure Supabase Storage before deploying uploads publicly."
    )


def upload_review_image(uploaded_file: Any) -> tuple[bool, str | None, str | None]:
    if uploaded_file is None:
        return True, None, None

    file_name = _safe_upload_name(uploaded_file.name)
    data = uploaded_file.getvalue()
    if not data:
        return False, None, "The uploaded image appears to be empty."

    client = get_supabase_client()
    if client is None:
        ok, path, message = _save_uploaded_image_locally(file_name, data)
        return ok, path, message

    storage_path = f"reviews/{file_name}"
    try:
        client.storage.from_(STORAGE_BUCKET).upload(
            storage_path,
            data,
            {"content-type": _content_type(file_name, getattr(uploaded_file, "type", None))},
        )
        public_url = client.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
        if not public_url:
            return False, None, "Image uploaded, but Supabase did not return a public URL."
        return True, public_url, None
    except Exception as exc:
        try:
            ok, path, message = _save_uploaded_image_locally(file_name, data)
            if ok:
                return True, path, (
                    f"Supabase Storage upload failed, so the image was saved locally for development. Details: {exc}"
                )
            return False, None, message
        except Exception as local_exc:
            return False, None, (
                f"Image upload failed. Supabase Storage error: {exc}. Local fallback error: {local_exc}."
            )
