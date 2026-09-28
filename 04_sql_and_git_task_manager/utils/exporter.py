"""Structured JSON Exporter for CLI Task Manager."""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Union

import config
from utils.logger import setup_logger

logger = setup_logger("TaskManager.Exporter")


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder handling date and datetime objects."""

    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def export_tasks_to_json(
    manager,
    output_filename: Union[str, Path] = "tasks_export.json",
    status_filter: Optional[str] = None,
) -> Path:
    """Export tasks and analytical metrics into a structured JSON file."""
    if isinstance(output_filename, str):
        if not output_filename.endswith(".json"):
            output_filename += ".json"
        target_path = config.EXPORT_DIR / output_filename
    else:
        target_path = output_filename

    target_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Exporting tasks to JSON at %s", target_path)

    tasks = manager.list_tasks(status=status_filter)
    metrics = manager.get_metrics_summary()
    categories = manager.get_category_breakdown()
    priorities = manager.get_priority_breakdown()

    export_payload = {
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "format_version": "1.0",
            "filter_applied": status_filter or "all",
            "total_exported": len(tasks),
        },
        "metrics_summary": metrics,
        "category_breakdown": categories,
        "priority_distribution": priorities,
        "tasks": [t.to_dict() for t in tasks],
    }

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2, cls=DateTimeEncoder)

    logger.info("Successfully exported %d tasks to %s", len(tasks), target_path)
    return target_path
