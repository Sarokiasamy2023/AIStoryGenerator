import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).parent
ALLURE_RESULTS_DIR = BASE_DIR / "allure-results"


def _to_millis(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def create_allure_step(name: str, status: str, start_time: datetime, stop_time: datetime) -> Dict[str, Any]:
    """Create a minimal Allure step structure using datetime objects."""
    return {
        "name": name,
        "status": status,
        "start": start_time,
        "stop": stop_time,
    }


def create_attachment_from_file(path: str, name: str, mime_type: str) -> Optional[Dict[str, Any]]:
    """Copy a file into allure-results and return an attachment descriptor."""
    src = Path(path)
    if not src.exists():
        return None

    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    target_name = f"{uuid.uuid4()}-attachment{src.suffix or ''}"
    target_path = ALLURE_RESULTS_DIR / target_name

    try:
        shutil.copy2(str(src), str(target_path))
    except Exception:
        return None

    return {
        "name": name,
        "type": mime_type,
        "source": target_name,
    }


def write_allure_result(
    test_name: str,
    full_name: Optional[str],
    status: str,
    start_time: datetime,
    stop_time: datetime,
    steps: List[Dict[str, Any]],
    labels: Optional[List[Dict[str, str]]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    parameters: Optional[List[Dict[str, str]]] = None,
    status_details: Optional[str] = None,
) -> str:
    """Write a minimal Allure result JSON file and return its path.

    This does not require the allure Python bindings; it just writes data in the
    format expected by the Allure CLI.
    """
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    test_uuid = str(uuid.uuid4())

    result: Dict[str, Any] = {
        "uuid": test_uuid,
        "name": test_name,
        "fullName": full_name or test_name,
        "status": status or "unknown",
        "stage": "finished",
        "start": _to_millis(start_time),
        "stop": _to_millis(stop_time),
        "steps": [],
        "labels": labels or [],
        "parameters": parameters or [],
    }

    if status_details:
        result["statusDetails"] = {"message": status_details}

    for step in steps:
        # Expect step["start"] and step["stop"] as datetime
        step_start = step.get("start", start_time)
        step_stop = step.get("stop", stop_time)
        result["steps"].append(
            {
                "name": step.get("name", "step"),
                "status": step.get("status", "passed"),
                "start": _to_millis(step_start),
                "stop": _to_millis(step_stop),
            }
        )

    if attachments:
        result["attachments"] = attachments

    file_path = ALLURE_RESULTS_DIR / f"{test_uuid}-result.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    return str(file_path)
