"""MCP server exposing Laya decision primitives as advisory tools.

Requires the optional dependency group laya[mcp]. The server defaults to
stdio. Set LAYA_MCP_TRANSPORT=streamable-http to serve local HTTP.
"""
from __future__ import annotations

import os
import threading
from typing import Any, Dict, Optional

from .advisory import run_autodev_advisory
from .presets import guard_questions, moderation_questions, triage_questions
from .router import Router

try:
    from mcp.server import MCPServer
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Laya MCP support requires: pip install 'laya[mcp]'") from exc


mcp = MCPServer(
    "Laya Decision Engine",
    instructions=(
        "Fast System-1 classification and triage. Outputs are advisory only; "
        "do not treat them as authorization for irreversible or privileged actions."
    ),
)

_ROUTER: Optional[Router] = None
_ROUTER_LOCK = threading.Lock()


def _truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def get_router() -> Router:
    """Build one process-wide Router and reuse resident checkpoints."""
    global _ROUTER
    if _ROUTER is not None:
        return _ROUTER
    with _ROUTER_LOCK:
        if _ROUTER is None:
            max_loaded = max(1, int(os.environ.get("LAYA_MAX_LOADED", "1")))
            _ROUTER = Router(
                device=os.environ.get("LAYA_DEVICE") or None,
                max_loaded=max_loaded,
                auto_task_detection=True,
                preload=_truthy("LAYA_PRELOAD", False),
            )
    return _ROUTER


@mcp.tool()
def route(
    state: Any,
    questions: Optional[Dict[str, Any]] = None,
    model: Optional[str] = None,
    task: Optional[str] = None,
    lang: Optional[str] = None,
) -> Dict[str, Any]:
    """Select the Laya checkpoint for a state without loading a model."""
    return dict(get_router().route(state, questions or {}, model=model, task=task, lang=lang))


@mcp.tool()
def predict(
    state: Any,
    questions: Dict[str, Any],
    model: Optional[str] = None,
    task: Optional[str] = None,
    lang: Optional[str] = None,
) -> Dict[str, Any]:
    """Run typed Laya questions. The result is predictive, not authorization."""
    result = get_router().predict(state, questions, model=model, task=task, lang=lang)
    result["authoritative"] = False
    return result


@mcp.tool()
def guard(prompt: str) -> Dict[str, Any]:
    """Classify prompt-injection / jailbreak signals as an advisory guardrail."""
    result = get_router().predict({"prompt": prompt}, guard_questions())
    result["authoritative"] = False
    return result


@mcp.tool()
def moderate(content: str) -> Dict[str, Any]:
    """Classify content-safety signals as an advisory moderation result."""
    result = get_router().predict({"post": content}, moderation_questions())
    result["authoritative"] = False
    return result


@mcp.tool()
def triage(message: str) -> Dict[str, Any]:
    """Classify a support/work message using Laya's triage preset."""
    result = get_router().predict({"message": message}, triage_questions())
    result["authoritative"] = False
    return result


@mcp.tool()
def autodev_advisory(context: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a fast non-authoritative AutoDev action/risk/review advisory."""
    return run_autodev_advisory(get_router(), context)


@mcp.tool()
def status() -> Dict[str, Any]:
    """Return local server/router status without running inference."""
    router = get_router()
    return {
        "service": "laya-mcp",
        "authoritative": False,
        "loaded_models": router.loaded,
        "max_loaded": router.max_loaded,
        "device": router.device,
    }


def main() -> None:
    transport = os.environ.get("LAYA_MCP_TRANSPORT", "stdio").strip().lower()
    if transport in {"http", "streamable_http", "streamable-http"}:
        mcp.run(
            transport="streamable-http",
            host=os.environ.get("LAYA_MCP_HOST", "127.0.0.1"),
            port=int(os.environ.get("LAYA_MCP_PORT", "8765")),
            stateless_http=True,
            json_response=True,
        )
        return
    if transport != "stdio":
        raise ValueError("LAYA_MCP_TRANSPORT must be 'stdio' or 'streamable-http'")
    mcp.run()


if __name__ == "__main__":
    main()
