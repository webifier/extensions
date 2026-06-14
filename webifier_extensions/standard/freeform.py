from __future__ import annotations

from typing import Any, ClassVar

from webifier.core.base import NodeContext, RendererModule


class FreeformRenderer(RendererModule):
    """Pass content through without any wrapper."""

    template: ClassVar[str] = ""
    META_KEYS: ClassVar[frozenset[str]] = frozenset({"kind", "template", "freeform"})

    def process(self, data: dict[str, Any], ctx: NodeContext, builder) -> dict[str, Any]:
        """Process children that need markdown rendering."""
        processed = {}
        for key, value in data.items():
            if key in self.META_KEYS:
                processed[key] = value
                continue
            if isinstance(value, str):
                processed[key] = builder.render_markdown(
                    value,
                    assets_src_dir=ctx.assets_src_dir,
                    assets_target_dir=ctx.assets_target_dir,
                )
            else:
                processed[key] = builder.process_node(value, ctx.child(key))
        return processed

    def render(self, data: dict[str, Any], ctx: NodeContext, builder) -> str:
        """Render freeform — just concatenate all content."""
        parts = []
        for key, value in data.items():
            if key in self.META_KEYS:
                continue
            if isinstance(value, str):
                parts.append(value)
        return "\n".join(parts)
