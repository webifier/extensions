from __future__ import annotations

from typing import Any, ClassVar

from webifier.core.base import NodeContext, RendererModule


class PageRenderer(RendererModule):
    """Render a full HTML page from an index dict."""

    template: ClassVar[str] = "page.html"
    META_KEYS: ClassVar[frozenset[str]] = frozenset(
        {
            "kind",
            "template",
            "title",
            "nav",
            "header",
            "footer",
            "meta",
            "config",
            "search",
            "style",
        }
    )

    def process(self, data: dict[str, Any], ctx: NodeContext, builder) -> dict[str, Any]:
        """Process all non-meta sections by dispatching to their renderers."""
        processed = {}
        sections_html = []

        for key, value in data.items():
            if key in self.META_KEYS:
                processed[key] = value
                continue
            # Each section is processed recursively
            section_html = builder.process_node(value, ctx.child(key))
            sections_html.append({"key": key, "html": section_html, "data": value})

        processed["_sections"] = sections_html

        # Resolve background images in header
        if "header" in processed and isinstance(processed["header"], dict):
            processed["header"] = builder.resolve_background(processed["header"], ctx)

        return processed
