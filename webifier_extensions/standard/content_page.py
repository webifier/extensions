from __future__ import annotations

from typing import Any, ClassVar

from webifier.core.base import NodeContext, RendererModule


class ContentPageRenderer(RendererModule):
    """Render a content page (markdown/notebook output wrapped in a page layout)."""

    template: ClassVar[str] = "content.html"
    META_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "kind",
            "template",
            "content",
            "metadata",
            "title",
            "nav",
            "footer",
            "config",
            "colab",
        }
    )

    def process(self, data: dict[str, Any], ctx: NodeContext, builder) -> dict[str, Any]:
        """Content pages are pre-rendered — just pass through."""
        return data
