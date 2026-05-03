from __future__ import annotations

import ast
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
NUMERIC_COLUMNS = {
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
}
HALF_POINT_COLUMNS = {
    "sweetness",
    "acidity",
    "aroma",
    "texture",
    "mango_intensity",
    "value_for_money",
    "final_score",
}


@st.cache_resource(show_spinner=False)
def _create_supabase_client(supabase_url: str, supabase_key: str) -> Client | None:
    try:
        return create_client(supabase_url, supabase_key)
    except Exception:
        st.error("Could not connect to Supabase. Check the configured URL and key.")
        return None


def get_supabase_client() -> Client | None:
    settings = get_settings()
    if not settings.has_supabase_credentials:
        return None

    return _create_supabase_client(settings.supabase_url, settings.supabase_key)


def get_admin_supabase_client() -> Client | None:
    settings = get_settings()
    if not settings.has_admin_credentials:
        return None

    return _create_supabase_client(settings.supabase_url, settings.supabase_service_role_key)


@st.cache_data(ttl=60, show_spinner=False)
def _load_reviews_cached(credential_signature: str, public_only: bool = True) -> tuple[pd.DataFrame, str | None]:
    _ = credential_signature
    client = get_supabase_client()
    if client is None:
        return pd.DataFrame(columns=REVIEW_COLUMNS), (
            "Supabase client could not be created even though credentials were found."
        )

    try:
        query = client.table("reviews").select("*").order("final_score", desc=True)
        if public_only:
            query = query.eq("public", True)
        response = query.execute()
    except Exception as exc:
        return pd.DataFrame(columns=REVIEW_COLUMNS), _human_error(exc, "load reviews")

    records = response.data or []
    if not records:
        return pd.DataFrame(columns=REVIEW_COLUMNS), None

    df = pd.DataFrame(records)
    for column in REVIEW_COLUMNS:
        if column not in df.columns:
            df[column] = None

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df[REVIEW_COLUMNS], None


def get_reviews(public_only: bool = True) -> tuple[pd.DataFrame, str | None]:
    if not public_only:
        return get_admin_reviews()

    settings = get_settings()
    if not settings.has_supabase_credentials:
        status = get_config_status()
        return pd.DataFrame(columns=REVIEW_COLUMNS), (
            "Supabase is not configured yet. Add SUPABASE_URL and SUPABASE_KEY or "
            "SUPABASE_ANON_KEY to .env locally or Streamlit secrets in deployment. "
            f"Current config: URL {status['SUPABASE_URL']}, key {status['SUPABASE_KEY']} "
            f"from {status['SUPABASE_KEY_SOURCE']}."
        )

    return _load_reviews_cached(settings.credential_signature, public_only)


def load_reviews() -> tuple[pd.DataFrame, str | None]:
    return get_reviews(public_only=True)


def get_admin_reviews() -> tuple[pd.DataFrame, str | None]:
    settings = get_settings()
    if not settings.has_admin_credentials:
        return pd.DataFrame(columns=REVIEW_COLUMNS), (
            "Admin writes are not configured. Add SUPABASE_SERVICE_ROLE_KEY to .env "
            "locally or Streamlit secrets in deployment."
        )

    client = get_admin_supabase_client()
    if client is None:
        return pd.DataFrame(columns=REVIEW_COLUMNS), "Admin Supabase client could not be created."

    try:
        response = client.table("reviews").select("*").order("created_at", desc=True).execute()
    except Exception as exc:
        return pd.DataFrame(columns=REVIEW_COLUMNS), _human_error(exc, "load reviews")

    records = response.data or []
    if not records:
        return pd.DataFrame(columns=REVIEW_COLUMNS), None

    df = pd.DataFrame(records)
    for column in REVIEW_COLUMNS:
        if column not in df.columns:
            df[column] = None

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df[REVIEW_COLUMNS], None


def _normalize_insert_value(key: str, value: Any) -> Any:
    if key not in NUMERIC_COLUMNS or value is None:
        return value

    if isinstance(value, float) and value.is_integer():
        return int(value)

    return value


def _clean_review_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: _normalize_insert_value(key, value)
        for key, value in payload.items()
        if key in REVIEW_COLUMNS and key not in {"id", "created_at"} and value != ""
    }


def _is_integer_schema_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "22p02" in message and "integer" in message


def _integer_schema_message() -> str:
    columns = ", ".join(sorted(HALF_POINT_COLUMNS))
    return (
        "Could not add review because the Supabase table still has integer score columns. "
        "Half-point scores need numeric columns. In Supabase SQL Editor, convert these "
        f"columns to numeric: {columns}."
    )


def _human_error(exc: Exception, action: str) -> str:
    raw_message = str(exc)
    details: dict[str, Any] = {}
    try:
        parsed = ast.literal_eval(raw_message)
        if isinstance(parsed, dict):
            details = parsed
    except (SyntaxError, ValueError):
        details = {}

    code = details.get("code")
    message = str(details.get("message") or raw_message).strip()

    if code == "42501" or "row-level security" in message.lower():
        return (
            f"Could not {action} because Supabase blocked the admin write. "
            "Check that SUPABASE_SERVICE_ROLE_KEY is configured correctly."
        )

    if code == "22P02" or "invalid input syntax" in message.lower():
        return f"Could not {action} because one field has a value the database cannot store."

    if action == "load reviews":
        return "Could not load reviews right now. Check the Supabase connection and read policy."

    return f"Could not {action}. Please check the Supabase configuration and try again."


def insert_review(payload: dict[str, Any]) -> tuple[bool, str]:
    client = get_admin_supabase_client()
    if client is None:
        return False, "Admin writes are not configured. Add SUPABASE_SERVICE_ROLE_KEY."

    if payload.get("final_score") in (None, ""):
        payload["final_score"] = calculate_final_score(payload)

    cleaned_payload = _clean_review_payload(payload)

    try:
        client.table("reviews").insert(cleaned_payload).execute()
        _load_reviews_cached.clear()
        return True, "Review added."
    except Exception as exc:
        if _is_integer_schema_error(exc):
            return False, _integer_schema_message()
        return False, _human_error(exc, "add review")


def update_review(review_id: str, payload: dict[str, Any]) -> tuple[bool, str]:
    client = get_admin_supabase_client()
    if client is None:
        return False, "Admin writes are not configured. Add SUPABASE_SERVICE_ROLE_KEY."

    if payload.get("final_score") in (None, ""):
        payload["final_score"] = calculate_final_score(payload)

    cleaned_payload = _clean_review_payload(payload)

    try:
        client.table("reviews").update(cleaned_payload).eq("id", review_id).execute()
        _load_reviews_cached.clear()
        return True, "Review updated."
    except Exception as exc:
        if _is_integer_schema_error(exc):
            return False, _integer_schema_message()
        return False, _human_error(exc, "update review")


def delete_review(review_id: str) -> tuple[bool, str]:
    client = get_admin_supabase_client()
    if client is None:
        return False, "Admin writes are not configured. Add SUPABASE_SERVICE_ROLE_KEY."

    try:
        client.table("reviews").delete().eq("id", review_id).execute()
        _load_reviews_cached.clear()
        return True, "Review deleted."
    except Exception as exc:
        return False, _human_error(exc, "delete review")


def save_review_coordinates(review_id: str, latitude: float, longitude: float) -> tuple[bool, str]:
    client = get_admin_supabase_client()
    if client is None:
        return False, "Coordinates cannot be saved automatically because SUPABASE_SERVICE_ROLE_KEY is missing."

    try:
        response = (
            client.table("reviews")
            .update({"latitude": latitude, "longitude": longitude})
            .eq("id", review_id)
            .is_("latitude", "null")
            .is_("longitude", "null")
            .execute()
        )
        _load_reviews_cached.clear()
        if not response.data:
            return False, "Coordinates were not saved because this review already has coordinates."
        return True, "Coordinates saved."
    except Exception as exc:
        return False, _human_error(exc, "save coordinates")


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

    client = get_admin_supabase_client()
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
                    "Image saved locally for development because cloud storage was not available."
                )
            return False, None, message
        except Exception as local_exc:
            _ = local_exc
            return False, None, (
                "We could not attach the uploaded image. You can save the review without an image."
            )
