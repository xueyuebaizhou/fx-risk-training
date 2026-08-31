from __future__ import annotations

from typing import Any


def upload_report_with_service_role(
    supabase_url: str,
    service_role_key: str,
    object_path: str,
    pdf_bytes: bytes,
    metadata: dict[str, Any],
) -> None:
    """可选云端存档；只允许服务端密钥调用，首版界面默认不启用。"""
    if not supabase_url or not service_role_key:
        raise ValueError("未配置新项目的 Supabase URL 或 Service Role Key。")
    from supabase import create_client

    client = create_client(supabase_url, service_role_key)
    client.storage.from_("training-reports").upload(
        object_path,
        pdf_bytes,
        {"content-type": "application/pdf", "upsert": "false"},
    )
    client.table("training_reports").insert(
        {**metadata, "object_path": object_path}
    ).execute()
