from __future__ import annotations

from typing import Any, ClassVar

from webifier.core.base import NodeContext, RendererModule


class LinksRenderer(RendererModule):
    """Render a list of links."""

    template: ClassVar[str] = "macros/links.html"
    META_KEYS: ClassVar[frozenset[str]] = frozenset({"kind", "template", "items"})

    def process(self, data: dict[str, Any], ctx: NodeContext, builder) -> dict[str, Any]:
        """Links are pre-processed by the builder's _process_link."""
        return data

    def render(self, data: dict[str, Any], ctx: NodeContext, builder) -> str:
        """Render links using the links macro."""
        template = builder.jinja_env.get_template("macros/links.html")
        return template.module.render_links(
            data.get("items", []),
            inline=ctx.depth > 1,
        )
