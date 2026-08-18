import re
from datetime import datetime
from pathlib import Path

from config import PLANS_BASE_FOLDER


def _slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[\s_]+", "-", text)
    return text[:40].strip("-") or "untitled"


def _markdown(result: dict, transcript: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    plan = result.get("plan", {})
    tags = ", ".join(result.get("tags", []))
    key_insights = plan.get("key_insights", [])
    action_steps = plan.get("action_steps", [])
    resources = plan.get("resources_needed", [])
    problems = plan.get("potential_problems", [])
    metrics = plan.get("success_metrics", [])

    lines = []
    lines.append(f"# {result.get('title', 'Untitled')}")
    lines.append("")
    lines.append(f"**Branch:** `{result.get('branch', 'uncategorized')}`")
    lines.append(f"**Date:** {today}")
    lines.append(f"**Confidence:** {result.get('confidence', 0)}")
    lines.append(f"**Tags:** {tags}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append(result.get("summary", ""))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Overview")
    lines.append(plan.get("overview", ""))
    lines.append("")
    lines.append("## Key Insights")
    lines.extend(f"- {i}" for i in key_insights)
    lines.append("")
    lines.append("## Action Steps")
    lines.extend(
        f"{s.get('step', idx + 1)}. **{s.get('task', '')}** — Priority: {s.get('priority', '')} | Time: {s.get('estimated_time', '')}"
        for idx, s in enumerate(action_steps)
    )
    lines.append("")
    lines.append("## Resources Needed")
    lines.extend(f"- {r}" for r in resources)
    lines.append("")
    lines.append("## Potential Problems")
    lines.extend(f"- {p}" for p in problems)
    lines.append("")
    lines.append("## Success Metrics")
    lines.extend(f"- {m}" for m in metrics)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Original Transcript")
    lines.append(transcript)
    lines.append("")
    return "\n".join(lines)


def save_plan(result: dict, transcript: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    branch = result.get("branch", "uncategorized")
    slug = _slugify(result.get("title", "untitled"))

    folder = PLANS_BASE_FOLDER / branch
    folder.mkdir(parents=True, exist_ok=True)

    filepath = folder / f"{today}-{slug}.md"
    filepath.write_text(_markdown(result, transcript), encoding="utf-8")
    return str(filepath)