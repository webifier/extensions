from __future__ import annotations

from typing import Any, ClassVar

from webifier.core.base import NodeContext, RendererModule


class LinksRenderer(RendererModule):
    """Render a list of links."""

    template: ClassVar[str] = "macros/links.html"
    META_KEYS: ClassVar[frozenset[str]] = frozenset({"kind", "template", "items", "content"})

    def process(self, data: dict[str, Any], ctx: NodeContext, builder) -> dict[str, Any]:
        """Process explicit `kind: links` items the same way bare lists are processed."""
        items = data.get("items", data.get("content", []))
        processed_items = []
        for i, item in enumerate(items):
            if isinstance(item, dict):
                processed_items.append(builder._process_link(item, ctx.child(str(i))))
            else:
                processed_items.append(item)
        processed = dict(data)
        processed["items"] = processed_items
        return processed

    def render(self, data: dict[str, Any], ctx: NodeContext, builder) -> str:
        """Render links using the links macro."""
        template = builder.jinja_env.get_template("macros/links.html")
        return template.module.render_links(
            data.get("items", []),
            inline=ctx.depth > 1,
        )
