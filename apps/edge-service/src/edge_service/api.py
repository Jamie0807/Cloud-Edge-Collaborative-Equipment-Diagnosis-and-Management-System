"""边端 HTTP 接入端点。"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from edge_service.service import EdgeService, FileValidationError

UTC = timezone.utc


def create_app(service: EdgeService) -> FastAPI:
    app = FastAPI(title="云边诊断边端服务", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "edge-service"}

    @app.post("/api/v1/terminal-heartbeats")
    def receive_heartbeat(payload: dict[str, Any]) -> dict[str, str]:
        try:
            return service.receive_heartbeat(payload, datetime.now(UTC))
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.post("/api/v1/detection-events")
    async def receive_detection(
        metadata: str = Form(...),
        file: UploadFile = File(...),  # noqa: B008
    ) -> dict[str, object]:
        try:
            decoded = json.loads(metadata)
            if not isinstance(decoded, dict):
                raise TypeError("metadata 必须是 JSON 对象")
            content = await file.read()
            return service.receive_detection(
                decoded,
                file.filename or "",
                file.content_type or "application/octet-stream",
                content,
            )
        except (ValueError, FileValidationError, json.JSONDecodeError) as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    return app


app = create_app(
    EdgeService(Path(os.getenv("EDGE_STORAGE_ROOT", "/tmp/diagnostics-edge-service")))
)
