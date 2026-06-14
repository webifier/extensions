from __future__ import annotations

from typing import Any, ClassVar

from webifier.core.base import NodeContext, RendererModule


class MarkdownRenderer(RendererModule):
    """Render a markdown string to HTML."""

    template: ClassVar[str] = ""  # No template — direct render
    META_KEYS: ClassVar[frozenset[str]] = frozenset({"kind", "template"})

    def process(self, data: dict[str, Any], ctx: NodeContext, builder) -> dict[str, Any]:
        return data

    def render(self, data: dict[str, Any], ctx: NodeContext, builder) -> str:
        """Render markdown content to HTML string."""
        raw = data.get("content", "")
        if not raw:
            return ""
        return builder.render_markdown(
            raw,
            assets_src_dir=ctx.assets_src_dir,
            assets_target_dir=ctx.assets_target_dir,
            search_links=ctx.search_links,
        )
